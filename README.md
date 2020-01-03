# JIRA predictor
JIRA ticket predictor

# Dataset

Get a jira dataset and unpack it
```bash
tar -xvf dataset_full.tar.gz
```

# Preprocess

* Update the file `users.yaml` with valid users.
* Run `preprocess.py`

# Training
* Use the notebook `jira.ipynb` or run the `train.py` file.

# Model serving
### Local serving
* Install requirements
```bash
pip install -r requirements-serving.txt
```
* Run
```bash
python serving.py
```
### Serving using Docker
* Build a docker image
```bash
docker build -t serving .
```
* Run it
```bash
docker run -it --rm -p 8080:8080 serving
```

### Test serving
* Run the `serving_test.py`

# LINKS

[ktrain](https://github.com/amaiya/ktrain)
