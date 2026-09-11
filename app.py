from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    ma_tache = {
        "titre": "Faire TP",
        "description": "Tests pytest",
        "date": "11-09-2026",
        "statut": "En cours",
        "priorite": "Haute"
    }

    return render_template('index.html', data=ma_tache)

if __name__ == '__main__':
    app.run(debug=True)