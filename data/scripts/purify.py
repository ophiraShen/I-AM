import json


def open_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield json.loads(line)

def write_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')

def purify_dialogue(dialogues):
    purified_dialogues = {}
    purified_dialogues['id'] = dialogues['id']
    purified_dialogues['dialogue'] = []
    

if __name__ == "__main__":
    for dialogue in open_jsonl('dialogues_grouped.jsonl'):
        print(dialogue)
