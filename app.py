from flask import Flask, render_template, request
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import unicodedata
import string
from difflib import get_close_matches

app = Flask(__name__)

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words("portuguese"))
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words and word not in string.punctuation]
    words = [unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('utf-8') for word in words]
    return " ".join(words)

def read_data_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = {}
    for line in lines:
        question, answer = line.strip().split(' | ')
        data[preprocess_text(question)] = answer

    return data

data = read_data_from_txt('data.txt')

def get_answer(question):
    question = preprocess_text(question)
    if question in data:
        return data[question]
    else:
        closest_match = get_close_matches(question, data.keys(), n=1, cutoff=0.5)
        if closest_match:
            return data[closest_match[0]]
        else:
            return "Desculpe, não encontrei uma resposta para a sua pergunta."

@app.route('/')
def index():
    return render_template('index.html', bot_response=None)

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    response = get_answer(user_input)
    return render_template('index.html', bot_response=response)

if __name__ == '__main__':
    app.run(debug=True)
