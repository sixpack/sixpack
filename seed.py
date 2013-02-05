import requests
import string
import random

experiments = {
    'show-bieber': ['yes', 'no'],
    'show-bieber': ['yes', 'no', 'call-me-maybe'],
    'blurry-buy-now': ['yes', 'no'],
    'button-color': ['blue', 'green', 'red', 'black', 'orange'],
    'solo-cup': ['red', 'green'],
    'jose': ['troll', 'no-troll']
}

# generate 20 client ids
client_ids = []
for i in range(1, 800):
    client_ids.append(''.join(random.choice(string.ascii_lowercase + string.digits + '-_') for x in range(30)))

client_exp = []
participations = {}
for x in range(1, 10):
    for experiment, alternatives in experiments.iteritems():
        _id = random.choice(client_ids)

        # no dupes, plz
        client_ids.remove(_id)

        client_exp.append((_id, experiment))

        payload = {'experiment': experiment, 'alternatives': alternatives, 'client_id': _id}
        ret = requests.get('http://localhost:5000/participate', params=payload)
        print ret.headers

for key, tup in enumerate(client_exp):
    if key % 2:
        client_id, exp = tup
        payload = {
            'experiment': exp,
            'client_id': client_id
        }
        ret = requests.get('http://localhost:5000/convert', params=payload)
        print ret.headers