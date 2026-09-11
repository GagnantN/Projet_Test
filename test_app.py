import json
import pytest

import app

@pytest.fixture
def client(tmp_path):
    """
    Prépare un environnement de test isolé.
    """

    # Fichier JSON temporaire créé par pytest
    fichier_test = tmp_path / "taches.json"

    # Données utilisées pour les tests
    taches_test = [
        {
            "id": 1,
            "titre": "Faire TP",
            "description": "Tests pytest",
            "date": "2026-09-11",
            "statut": "En cours",
            "priorite": "Haute"
        },
        {
            "id": 2,
            "titre": "Apprendre Flask",
            "description": "Créer une petite application",
            "date": "2026-09-12",
            "statut": "À faire",
            "priorite": "Moyenne"
        },
        {
            "id": 3,
            "titre": "Manger",
            "description": "J'ai faim",
            "date": "2026-09-26",
            "statut": "Terminé",
            "priorite": "Moyenne"
        }
    ]

    # Écrire les données dans le fichier temporaire
    fichier_test.write_text(
        json.dumps(taches_test, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

    # Utiliser ce fichier pendant les tests
    app.FICHIER_TACHES = str(fichier_test)

    # Activer le mode test
    app.app.config["TESTING"] = True

    # Créer le client Flask
    with app.app.test_client() as client:
        yield client


def test_afficher_taches(client):

    """
    CT-VIEW-01 
    Vérifie que la page principale affiche les tâches. 
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b"Faire TP" in response.data
    assert b"Apprendre Flask" in response.data
    assert b"Manger" in response.data



def test_creation_tache_valide(client):
    """
    CT-CREAT-01
    Vérifie qu'une tâche valide est correctement créée.
    """

    response = client.post(
        "/ajouter",
        data={
            "titre": "Nouvelle tâche",
            "description": "Ma nouvelle tâche de test",
            "date": "2026-10-01"
        }
    )

    # La création doit rediriger vers la page principale
    assert response.status_code == 302

    # Recharger les tâches
    taches = app.charger_taches()

    # Vérifier que la nouvelle tâche existe
    assert len(taches) == 4

    nouvelle_tache = taches[-1]

    assert nouvelle_tache["titre"] == "Nouvelle tâche"
    assert nouvelle_tache["description"] == "Ma nouvelle tâche de test"
    assert nouvelle_tache["date"] == "2026-10-01"

    # Vérifier les valeurs par défaut
    assert nouvelle_tache["statut"] == "À faire"
    assert nouvelle_tache["priorite"] == "Moyenne"


def test_creation_tache_sans_titre(client):
    """
    CT-CREAT-02
    Vérifie qu'une tâche sans titre n'est pas créée.
    """

    response = client.post(
        "/ajouter",
        data={
            "titre": "",
            "description": "Description de test",
            "date": "2026-10-01"
        }
    )

    # L'application doit rediriger vers la page principale
    assert response.status_code == 302

    # Vérifier que le nombre de tâches n'a pas changé
    taches = app.charger_taches()

    assert len(taches) == 3


def test_terminer_tache(client):
    """
    CT-TERM-01
    Vérifie qu'une tâche passe au statut "Terminé".
    """

    response = client.post(
        "/terminer/1",
        data={
            "filtre": "toutes"
        }
    )

    assert response.status_code == 302

    taches = app.charger_taches()

    tache = next(t for t in taches if t["id"] == 1)

    assert tache["statut"] == "Terminé"



def test_terminer_tache_inexistante(client):
    """
    CT-TERM-02
    Vérifie qu'une tâche inexistante ne provoque pas de crash.
    """

    response = client.post(
        "/terminer/999",
        data={
            "filtre": "toutes"
        }
    )

    assert response.status_code == 302

    taches = app.charger_taches()

    assert len(taches) == 3


def test_filtre_taches_actives(client):
    """
    CT-FILT-01
    Vérifie que le filtre "actives" exclut les tâches terminées.
    """

    response = client.get("/?filtre=actives")

    assert response.status_code == 200

    assert b"Faire TP" in response.data
    assert b"Apprendre Flask" in response.data

    assert b"Manger" not in response.data


def test_filtre_invalide(client):
    """
    CT-FILT-02
    Vérifie qu'un filtre inconnu revient au filtre "toutes".
    """

    response = client.get("/?filtre=blabla")

    assert response.status_code == 200

    # Toutes les tâches doivent être affichées
    assert b"Faire TP" in response.data
    assert b"Apprendre Flask" in response.data
    assert b"Manger" in response.data

    # Le filtre doit être revenu à "toutes"
    assert b'class="actif">Toutes</a>' in response.data



def test_supprimer_tache(client):
    """
    CT-SUPPR-01
    Vérifie qu'une tâche existante est correctement supprimée.
    """

    response = client.post(
        "/supprimer/2",
        data={
            "filtre": "toutes"
        }
    )

    assert response.status_code == 302

    taches = app.charger_taches()

    # Il doit rester 2 tâches
    assert len(taches) == 2

    # La tâche numéro 2 ne doit plus exister
    assert not any(t["id"] == 2 for t in taches)



def test_supprimer_tache_inexistante(client):
    """
    CT-SUPPR-02
    Vérifie que la suppression d'une tâche inexistante
    ne provoque pas de crash.
    """

    response = client.post(
        "/supprimer/999",
        data={
            "filtre": "toutes"
        }
    )

    assert response.status_code == 302

    taches = app.charger_taches()

    # Les 3 tâches doivent toujours être présentes
    assert len(taches) == 3

