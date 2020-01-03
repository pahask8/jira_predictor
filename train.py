import os
import logging
import shutil
from pathlib import Path

import ktrain
from ktrain import text as txt


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

datasets_full = "dataset_preprocess"

users = os.listdir(datasets_full)

Path(os.path.join("jiradata", "test")).mkdir(parents=True, exist_ok=True)
Path(os.path.join("jiradata", "train")).mkdir(parents=True, exist_ok=True)

for user in users:
    # get list of files
    tickets = os.listdir(os.path.join(datasets_full, user))

    test = tickets[:len(tickets) // 2]
    train = tickets[len(tickets) // 2:]

    # copy test
    for ticket in test:
        Path(os.path.join("jiradata", "test", user)).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(datasets_full, user, ticket), os.path.join("jiradata", "test", user, ticket))

    # copy test
    for ticket in test:
        Path(os.path.join("jiradata", "train", user)).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(datasets_full, user, ticket), os.path.join("jiradata", "train", user, ticket))

# load data
(x_train, y_train), (x_test, y_test), preproc = txt.texts_from_folder('jiradata', maxlen=500,
                                                                      preprocess_mode='bert',
                                                                      train_test_names=['train', 'test'],
                                                                      classes=users)
# load model
model = txt.text_classifier('bert', (x_train, y_train), preproc=preproc)

# wrap model and data in ktrain.Learner object
learner = ktrain.get_learner(model,
                             train_data=(x_train, y_train),
                             val_data=(x_test, y_test),
                             batch_size=10)

# find good learning rate
learner.lr_find()  # briefly simulate training to find good learning rate
learner.lr_plot()  # visually identify best learning rate

# # employs a triangular learning rate policy with automatic stopping
learner.autofit(0.000029, 10)

predictor = ktrain.get_predictor(learner.model, preproc)
predictor.save('model/model')
LOG.info("Model has been saved")

# Saving Model
model_json = learner.model.to_json()
with open("model/model.json", "w") as json_file:
    json_file.write(model_json)

learner.model.save_weights("model/model.h5")
LOG.info("Model weights have been saved")
