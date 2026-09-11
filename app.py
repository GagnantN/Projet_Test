from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def home():
    with open('taches.json', 'r', encoding='utf-8') as fichier:
        taches = json.load(fichier)

    return render_template('index.html', taches=taches)

if __name__ == '__main__':
    app.run(debug=True)