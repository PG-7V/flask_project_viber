
import json
print('-----------')

with open('cat.json') as f_j:
    data_j = json.load(f_j)

    print(data_j)