import pickle
from codecs import open
from flask import Flask, render_template, request

from vectorizer import Vectorizer

app = Flask(__name__)

with open('classifier.pickle', 'rb') as f:
    classifier = pickle.load(f)

with open('vectorizer.pickle', 'rb') as f:
    vectorizer = pickle.load(f)

@app.route("/demo", methods=["POST", "GET"])
def index_page(text="", prediction_message=""):
    if request.method == "POST":
        text = request.form["text"]
        prediction_message = classifier.classify(vectorizer.get_features(text))

    return render_template('demo.html', text=text, prediction_message=prediction_message)


if __name__ == "__main__":
    app.run(host='localhost', port=80, debug=False)
