import numpy as np
import re
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
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


# Testing prediction
print(prediction_input_processing(
    'Americans are more concerned over Indians fake open source contribution'))
