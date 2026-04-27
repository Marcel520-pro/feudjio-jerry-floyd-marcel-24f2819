from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reponse(db.Model):
    __tablename__ = 'reponses'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Text)
    ville = db.Column(db.Text)
    statut = db.Column(db.Text)
    connexion = db.Column(db.Text)
    tentative_game = db.Column(db.Text)
    moteur = db.Column(db.Text)
    apprentissage = db.Column(db.Text)
    publie = db.Column(db.Text)
    score_frein_materiel = db.Column(db.Integer)
    score_frein_connexion = db.Column(db.Integer)
    score_frein_formation = db.Column(db.Integer)
    score_frein_monetisation = db.Column(db.Integer)
    score_frein_familial = db.Column(db.Integer)
    aide_souhaitee = db.Column(db.Text)
    theme_reve = db.Column(db.Text)

    minigame = db.relationship('Minigame', backref='reponse', uselist=False)


class Minigame(db.Model):
    __tablename__ = 'minigame'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('reponses.id'))
    scenario1_choix = db.Column(db.Text)
    scenario2_choix = db.Column(db.Text)
    scenario3_choix = db.Column(db.Text)
    score_resilience = db.Column(db.Integer)
    diagnostic = db.Column(db.Text)
