import json
dict_ = {'person':{'height': 170, 'width': 60},
         'head':{'height': 40, 'width': 20}}
j = json.dumps(dict_, indent = 4)
with open("object_size.json", "w") as f:
    json.dump(dict_, f, indent = 4)
print(dict_['person'])
print(dict_['head'])
