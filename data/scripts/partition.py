# data/scripts/partition.py
# 数据集划分, 按照80%、10%、10%的比例划分成训练集、验证集和测试集。
import sys
import os
from collections import defaultdict
import random
import json


def split_datasets(dialogues):
    # 按category分组
    categories = defaultdict(list)
    for dialogue in dialogues:
        length = len(dialogue['dialogue'])
        if length <= 5:
            length_group = 'short'
        elif length <= 8:
            length_group = 'medium'
        else:
            length_group = 'long'
        category = f"{dialogue['group']}_{length_group}"
        categories[category].append(dialogue)
    
    train, val, test = [], [], []
    
    # 对每个category进行划分
    for category, items in categories.items():
        n_samples = len(items)
        
        if n_samples >= 50:  # 数据充足的类别
            # 标准 80:10:10 划分
            n_test = int(n_samples * 0.1)
            n_val = n_test
            n_train = n_samples - n_test - n_val
            
        elif n_samples >= 20:  # 数据适中的类别
            # 70:15:15 划分，保证验证集和测试集有足够样本
            n_test = int(n_samples * 0.15)
            n_val = n_test
            n_train = n_samples - n_test - n_val
            
        else:  # 数据稀少的类别
            # 确保验证集和测试集至少各有1个样本
            n_test = max(1, int(n_samples * 0.2))
            n_val = n_test
            n_train = n_samples - n_test - n_val
        
        # 随机打乱并划分
        shuffled = random.sample(items, n_samples)
        train.extend(shuffled[:n_train])
        val.extend(shuffled[n_train:n_train+n_val])
        test.extend(shuffled[n_train+n_val:])
    
    return train, val, test


def save_partitions(train, val, test):
    # 保存到data/partitions目录下   
    current_dir = os.path.dirname(os.path.abspath(__file__))
    partitions_dir = os.path.join(current_dir, '..', 'partitions')
    os.makedirs(partitions_dir, exist_ok=True)
    with open(os.path.join(partitions_dir, 'train.jsonl'), 'w', encoding='utf-8') as f:
        for dialogue in train:
            f.write(json.dumps(dialogue, ensure_ascii=False) + '\n')
    with open(os.path.join(partitions_dir, 'val.jsonl'), 'w', encoding='utf-8') as f:
        for dialogue in val:
            f.write(json.dumps(dialogue, ensure_ascii=False) + '\n')
    with open(os.path.join(partitions_dir, 'test.jsonl'), 'w', encoding='utf-8') as f:
        for dialogue in test:
            f.write(json.dumps(dialogue, ensure_ascii=False) + '\n')
    
def load_data(file_path):
    dialogues = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            dialogues.append(json.loads(line))
    return dialogues

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(os.path.dirname(current_dir), 'dialogues_grouped.jsonl')
    dialogues = load_data(data_file)
    train, val, test = split_datasets(dialogues)
    save_partitions(train, val, test)
    
    