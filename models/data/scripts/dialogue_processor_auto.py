# data/scripts/dialogue_processor_auto.py

import json
import os

def process_dialogues(input_file, output_file):
    # 读取数据集
    datasets = []
    with open(input_file, 'r') as f:
        for line in f:
            datasets.append(json.loads(line))

    # 处理对话数据
    for data in datasets:
        dialogue = data['dialogue']
        tmp = []
        for i in range(len(dialogue)-1):
            if dialogue[i]['role'] == "user" and dialogue[i+1]['role'] == "assistant":
                # 创建对话历史列表
                dialogue_history = []
                
                # 添加所有直到当前回合的对话
                for j in range(i + 1):
                    dialogue_history.append({
                        "role": dialogue[j]['role'],
                        "content": dialogue[j]['content']
                    })
                    
                # 使用 json.dumps 来正确序列化整个对话历史
                inputs = json.dumps(dialogue_history, ensure_ascii=False)
                outputs = json.dumps({
                    "role": dialogue[i+1]['role'],
                    "content": dialogue[i+1]['content']
                }, ensure_ascii=False)
                
                tmp.append({"input": inputs, "output": outputs})
                
        # 写入处理后的数据
        with open(output_file, 'a') as f:
            for d in tmp:
                f.write(json.dumps(d, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(__file__), '../partitions/val_dialogues.jsonl')
    output_file = os.path.join(os.path.dirname(__file__), '../val.jsonl')
    process_dialogues(input_file, output_file)