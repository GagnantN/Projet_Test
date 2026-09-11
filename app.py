from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# -------------------- Fichier Base de données -------------------- #
FICHIER_TACHES = 'taches.json'


# -------------------- Fonction Charger Tâches -------------------- #
def charger_taches():
    # Lit taches.json et renvoie la liste des tâches
    if not os.path.exists(FICHIER_TACHES):
        return []
    try:
        with open(FICHIER_TACHES, 'r', encoding='utf-8') as fichier:
            taches = json.load(fichier)
    except (json.JSONDecodeError, ValueError):
        return []

    if not isinstance(taches, list):
        return []
    return taches
# ----------------------------------------------------------------- #


# ------------------ Fonction Sauvegarder Tâches ------------------ #
def sauvegarder_taches(taches):
    # Écrit la liste des tâches dans taches.json
    with open(FICHIER_TACHES, 'w', encoding='utf-8') as fichier:
        json.dump(taches, fichier, ensure_ascii=False, indent=4)
# ----------------------------------------------------------------- #


# ----------------- Fonction Calculer Prochain ID ----------------- #
def prochain_id(taches):
    # Calcule le prochain id disponible : le plus grand id existant + 1
    if not taches:
        return 1
    return max(tache['id'] for tache in taches) + 1
# ----------------------------------------------------------------- #


# -------------------- Fonction Afficher tâches ------------------- #
@app.route('/')
def home():
    taches = charger_taches()
    filtre = request.args.get('filtre', 'toutes')
    erreur = request.args.get('erreur')

    if filtre == 'actives':
        taches_affichees = [t for t in taches if t.get('statut') != 'Terminé']
    elif filtre == 'terminees':
        taches_affichees = [t for t in taches if t.get('statut') == 'Terminé']
    else:
        filtre = 'toutes'
        taches_affichees = taches

    return render_template(
        'index.html',
        taches=taches_affichees,
        filtre=filtre,
        erreur=erreur,
    )
# ----------------------------------------------------------------- #


# -------------------- Fonction Ajouter Tâche --------------------- #
@app.route('/ajouter', methods=['POST'])
def ajouter():
    # Crée une nouvelle tâche à partir du formulaire
    titre = request.form.get('titre', '').strip()
    description = request.form.get('description', '').strip()
    date = request.form.get('date', '').strip()

    # Titre et date obligatoires
    if not titre or not date:
        return redirect(url_for('home', erreur='champs_vides'))

    taches = charger_taches()
    nouvelle_tache = {
        'id': prochain_id(taches),
        'titre': titre,
        'description': description,
        'date': date,
        'statut': 'À faire',
        'priorite': 'Moyenne',
    }
    taches.append(nouvelle_tache)
    sauvegarder_taches(taches)
    return redirect(url_for('home'))
# ----------------------------------------------------------------- #


# -------------------- Fonction Tâche Terminer -------------------- #
@app.route('/terminer/<int:tache_id>', methods=['POST'])
def terminer(tache_id):
    # Marque la tâche `tache_id` comme "Terminé
    taches = charger_taches()
    for tache in taches:
        if tache['id'] == tache_id:
            tache['statut'] = 'Terminé'
            break
    sauvegarder_taches(taches)
    return redirect(url_for('home', filtre=request.form.get('filtre', 'toutes')))
# ----------------------------------------------------------------- #


# ------------------- Fonction Supprimer Tâche -------------------- #

@app.route('/supprimer/<int:tache_id>', methods=['POST'])
def supprimer(tache_id):
    taches = charger_taches()
    taches = [t for t in taches if t['id'] != tache_id]
    sauvegarder_taches(taches)
    return redirect(url_for('home', filtre=request.form.get('filtre', 'toutes')))
# ----------------------------------------------------------------- #



if __name__ == '__main__':
    app.run(debug=True)
