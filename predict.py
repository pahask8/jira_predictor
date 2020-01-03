import os
import random
import time

import ktrain

predictor = ktrain.load_predictor('predictor')

count = 0

while count < 20:
    user = random.choice(os.listdir("jiradata/train"))
    ticket = random.choice(os.listdir(f"jiradata/train/{user}"))
    ticket_path = os.path.join(f"jiradata/train/{user}", ticket)
    with open(ticket_path, 'r') as f:
        doc = f.read()
    predict = predictor.predict(doc)
    print("predicted user: ", predict, "ticket: ", ticket_path)
    print(predict == user)
    time.sleep(1)
    count = count + 1
