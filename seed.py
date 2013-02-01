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
for i in range(1, 20):
    client_ids.append(''.join(random.choice(string.ascii_lowercase + string.digits + '-_') for x in range(30)))

participations = {}
for x in range(1, 10):
    for experiment, alternatives in experiments.iteritems():
        _id = random.choice(client_ids)
        payload = {'experiment': experiment, 'alternatives': alternatives, 'client_id': _id}
        ret = requests.get('http://localhost:5000/participate', params=payload)
        print ret.headers

