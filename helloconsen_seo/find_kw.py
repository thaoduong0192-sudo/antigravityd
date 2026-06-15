import json
db = json.load(open('b2b_database.json', encoding='utf-8'))
for k in db['keywords']:
    if 'petpro' in k.lower():
        print(k)
