import os
import re
import urllib.request
from flask import *
import sqlite3
from werkzeug.utils import secure_filename

import numpy as np
import re
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
app = Flask(__name__)

app.secret_key = "secret key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/logon')
def logon():
    return render_template('signup.html')


@app.route("/signup", methods=["post"])
def signup():
    username = request.form['user']
    name = request.form['name']
    email = request.form['email']
    number = request.form["mobile"]
    password = request.form['password']
    role = "student"
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`,'role') VALUES (?, ?, ?, ?, ?,?)",
                (username, email, password, number, name, role))
    con.commit()
    con.close()
    return render_template("index.html")


@app.route("/signin", methods=["post"])
def signin():
    mail1 = request.form['user']
    password1 = request.form['password']
    con = sqlite3.connect('signup.db')
    data = 0
    data = con.execute(
        "select `user`, `password`,role from info where `user` = ? AND `password` = ?", (mail1, password1,)).fetchall()
    print(data)
    if mail1 == 'admin' and password1 == 'admin':
        session['username'] = "admin"
        return redirect("userlogin")
    elif mail1 == str(data[0][0]) and password1 == str(data[0][1]):
        print(data)
        session['username'] = data[0][0]
        return redirect("userlogin")
    else:
        return render_template("signup.html")


@app.route("/userlogin")
def userlogin():
    return render_template("student.html")


max_length = 40
embedded_features = 40

# Text cleaning regex pattern
text_cleaning = r'\b0\S*|\b[^A-Za-z0-9]+'


def preprocess_filter(text):
    text = re.sub(text_cleaning, " ", str(text).lower().strip())
    return text

# Function for one-hot encoding


def one_hot_encoded(text, vocab_size=5000):
    hot_encoded = one_hot(text, vocab_size)
    return hot_encoded


def word_embedding(text):
    preprocessed_text = preprocess_filter(text)
    hot_encoded = one_hot_encoded(preprocessed_text)
    return hot_encoded

    # Load the trained model
model = load_model("cnnmodel.h5")
# input generator


def prediction_input_processing(text):
    encoded = word_embedding(text)
    padded_encoded_title = pad_sequences(
        [encoded], maxlen=max_length, padding='pre')
    output = model.predict(padded_encoded_title)
    output = np.where(0.4 > output, 1, 0)
    if output[0][0] == 1:
        return 'Yes this News is fake'
    return 'No, It is not fake'


@app.route('/predict', methods=["POST"])
def predict():
    y = request.form["t"]
    t = prediction_input_processing(y)
    return render_template("student.html", t=t)


@app.route('/logout')
def home():
    session.pop('username', None)
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
