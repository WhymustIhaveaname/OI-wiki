# import yaml # 垃圾包, 没有跳过错误的选项并且超级慢
import os
import re

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_yml(file_path):
    "读取 mkdocs.yml 文件, 返回目录, 目录的每一条是 (层级, 标题, 路径)"
    menu = []
    content_flag = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for l in file:
            if l.startswith('nav:'):
                content_flag = True
            if content_flag and l.strip().startswith('-'):
                level = l.split('-')[0]
                level = len(level)//2-1
                *title, path = l.strip().lstrip('-').split(':')
                title = ":".join(title)
                menu.append((level, title.strip(), path.strip()))
            if l.startswith('theme:'):
                content_flag = False
                break

    return menu

def wash_question(question):
    return re.sub("^\+*\s*note\s*", "", question).strip()

def wash_code(code):
    codes = re.findall(r"```(.+?)\n(.*?)```", code, re.DOTALL)
    ret   = []
    for lang, text in codes:
        file = re.search(r'--8<-- "(.+?)"', text)
        if file:
            text = read_file(file.group(1))
        ret.append({
            "lang": lang,
            "text": text
        })
    return ret

def get_exercise(content):
    "从 content 中用 re 提取习题, 思路是将文档按 ??? 拆分, 参考代码之前的就是解题思路或者题目"
    content_list = re.split(r"\?\?\?", content)
    questions = []
    this_question = None
    for i, text in enumerate(content_list):
        if text.startswith("+ note"):
            if this_question is not None and (len(this_question["plan"]) >0 or len(this_question["code"]) >0):
                questions.append(this_question)
                this_question = None
            this_question = {
                "question": wash_question(text),
                "plan": "",
                "code": []
            }
        if this_question is None:
            continue
        elif "解题思路" in text:
            this_question["plan"] += wash_question(text)
        elif "参考代码" in text:
            this_question["code"] += wash_code(text)
    if this_question is not None and (len(this_question["plan"]) >0 or len(this_question["code"]) >0):
        questions.append(this_question)
    return questions

if __name__ == "__main__":
    token_count = 0
    questions_count = 0
    menu = parse_yml("mkdocs.yml")
    for level,title,path in menu:
        if len(path) == 0:
            continue

        content   = read_file(os.path.join("./docs",path))
        questions = get_exercise(content)

        token_count += len(content)

        print(level,title,path)
        for question in questions:
            print(question)
            questions_count += 1

    print("token_count:", token_count)
    print("questions_count:", questions_count)
