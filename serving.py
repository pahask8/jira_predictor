import logging

from flask import Flask, request, jsonify
import ktrain

import tensorflow as tf
from tensorflow.python.keras.backend import set_session

import yaml

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)

USERS_FILE = "users.yaml"

IGNORED_COMPONENT_NAMES = [
    "i'm not sure",
]

GRAPH = None
SESS = None
PREDICTOR = None


def load_predictor():
    global SESS
    SESS = tf.Session()
    set_session(SESS)

    # load the model, and pass in the custom metric function
    global GRAPH
    GRAPH = tf.get_default_graph()

    global PREDICTOR
    PREDICTOR = ktrain.load_predictor('model/model')
    if hasattr(PREDICTOR.model, '_make_predict_function'):
        PREDICTOR.model._make_predict_function()


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['message'] = self.message
        return result


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/predict', methods=['POST'])
def predict():
    """
    Example of data:

    {
      "fields": {
        "components": [
          {
            "name": "CI/CD"
          }
        ],
        "project": {
          "name": "Project name"
        },
        "description": "Some description",
        "summary": "Some summary"
      }
    }

    :return: Predicted user
    """
    text = request.json
    LOG.debug('Going to predict the data, data: %s', text)

    post_example = {
        "fields": {
            "components": [
                {
                    "name": "CI/CD"
                }
            ],
            "project": {
                "name": "Project name"
            },
            "description": "Some description",
            "summary": "Some summary"
        }
    }

    try:
        # project
        project_name = text['fields']['project']['name']

        # components
        components = sorted(
            list(set([_['name'].lower() for _ in text['fields']['components'] if _ not in IGNORED_COMPONENT_NAMES])))
        components_name = ", ".join(components)

        # description
        description = text['fields']['description']

        # summary
        summary = text['fields']['summary']

        doc = f"{project_name} {components_name} {description} {summary}".lower()
    except KeyError as error:
        raise InvalidUsage(
            f'Cannot get a mandatory key in the post data, error: {error}, example of post data: {post_example}',
            status_code=405)

    LOG.info("Going to use the following text for prediction: '%s'", doc)
    with GRAPH.as_default():
        set_session(SESS)
        predicted_user = PREDICTOR.predict(doc)
        predicted_user_full_name = active_users[predicted_user]
        LOG.info("Predicted user: %s, fullname: %s", predicted_user, predicted_user_full_name)
        return jsonify(
            {
                'login': predicted_user,
                'fullname': predicted_user_full_name,
                'status': 'ok'
            }
        )


@app.route('/health', methods=['GET'])
def health():
    result = {
        'status': 'ok'
    }

    with open(USERS_FILE, 'r') as f:
        result['users'] = yaml.load(f, Loader=yaml.FullLoader)

    with GRAPH.as_default():
        set_session(SESS)
        result['classes'] = PREDICTOR.get_classes()

    return jsonify(result)


@app.route('/', methods=['GET'])
def index():
    return "Jira predictor"


if __name__ == "__main__":
    load_predictor()
    with open(USERS_FILE, 'r') as f:
        users = yaml.load(f, Loader=yaml.FullLoader)
        active_users = users['active']
    app.run(host='0.0.0.0', port=8080)
    app.run()
