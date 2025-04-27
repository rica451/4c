import os
import json

outout_path = '/workspace/cold/merged_data.json'
source_path = '/workspace/cold/data_generation'

convo_list = []

for file in os.listdir(source_path):
    if 'ancient' in file:
        json_file = os.path.join(source_path, file)
        convos = json.load(open(json_file, 'r', encoding='utf-8'))
        for convo in convos:
            converted_convo = {"messages" : []}
            for message in convo['conversations']:
                converted_convo['messages'].append({
                    "role": message['from'],
                    "content": message['value']
                })
            convo_list.append(converted_convo)

with open(outout_path, 'w', encoding='utf-8') as f:
    json.dump(convo_list, f, ensure_ascii=False, indent=4)