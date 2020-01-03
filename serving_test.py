import os
import logging
import random
import json
import requests

logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)

url = "http://0.0.0.0:8080/predict"
# while True:
ticket = random.choice(os.listdir("dataset_full"))
ticket_path = os.path.join("dataset_full", ticket)

with open(ticket_path, 'r') as f:
    data = json.loads(f.read())

print(data)
print(ticket_path)

r = requests.post(url=url, json=data)
print(r.json())
