import json

data_j = json.load(open('cat.json'))

for product in data_j['products']:
    link = json.loads(product['gallery'])[0]['img']
    print(link)
