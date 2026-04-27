import csv
import io
import json
import threading
import requests as http_requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from app.models.database import db, Reponse, Minigame

# ─── Config Telegram ─────────────────────────────────────────────────────────
TELEGRAM_TOKEN  = "8353735487:AAGxArdm_bkTPaKVPusRjJLCf-WEs8JwFiU"
TELEGRAM_CHAT_ID = "8781577019"

def send_telegram(message: str):
    """Envoie un message Telegram en arrière-plan (non bloquant)."""
    def _send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            http_requests.post(url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }, timeout=8)
        except Exception as e:
            print(f"[Telegram] Erreur envoi : {e}")
    threading.Thread(target=_send, daemon=True).start()

bp = Blueprint('main', __name__)

# ─── Scénarios du mini-jeu ───────────────────────────────────────────────────
SCENARIOS = [
    {
        "id": 1,
        "titre": "La coupure de courant",
        "contexte": "Tu es à mi-chemin dans le développement de ton jeu RPG. Il est 23h, tu viens d'écrire 300 lignes de code parfait. Soudain... le courant s'en va. Ton PC s'éteint. Tu n'avais pas sauvegardé.",
        "question": "Que fais-tu ?",
        "choix": [
            {"id": "A", "texte": "Tu abandonnes le projet. Ce pays ne te mérite pas.", "emoji": "<i class='bi bi-emoji-angry'></i>"},
            {"id": "B", "texte": "Tu attends que le courant revienne et tu recommences calmement.", "emoji": "<i class='bi bi-emoji-smile'></i>"},
            {"id": "C", "texte": "Tu passes en mode offline, notes tout sur papier et profites pour planifier.", "emoji": "<i class='bi bi-pencil-square'></i>"},
        ]
    },
    {
        "id": 2,
        "titre": "Le refus familial",
        "contexte": "Tu annonces à ta famille que tu veux créer un studio de jeux vidéo au lieu de chercher un travail \"sérieux\". Ton père sort la citation classique : \"Les jeux vidéo, c'est pour les enfants. Va chercher un vrai emploi.\"",
        "question": "Tu réagis comment ?",
        "choix": [
            {"id": "A", "texte": "Tu ranges ton laptop et tu postules dans une banque.", "emoji": "<i class='bi bi-bank'></i>"},
            {"id": "B", "texte": "Tu fais semblant d'accepter mais tu continues en secret.", "emoji": "<i class='bi bi-incognito'></i>"},
            {"id": "C", "texte": "Tu prépares une présentation avec chiffres et exemples de succès africains pour convaincre.", "emoji": "<i class='bi bi-lightbulb'></i>"},
        ]
    },
    {
        "id": 3,
        "titre": "Le manque de ressources",
        "contexte": "Tu as une idée brillante pour un jeu mobile sur la mythologie bamiléké. Mais tu n'as pas d'ordinateur puissant, pas de budget pour les assets, et l'internet coûte cher.",
        "question": "Comment tu avances ?",
        "choix": [
            {"id": "A", "texte": "Tu attends d'avoir les moyens. Un jour peut-être...", "emoji": "<i class='bi bi-hourglass-split'></i>"},
            {"id": "B", "texte": "Tu utilises un moteur léger comme GDevelop sur téléphone et des assets gratuits.", "emoji": "<i class='bi bi-phone'></i>"},
            {"id": "C", "texte": "Tu formes une équipe locale, chacun apporte sa compétence, vous mutualisez les ressources.", "emoji": "<i class='bi bi-people'></i>"},
        ]
    },
]

DIAGNOSTICS = {
    0: ("Débutant Résistant <i class='bi bi-brightness-alt-high'></i>", "Les obstacles semblent insurmontables pour l'instant. Mais chaque grand dev a commencé quelque part. La communauté CamGame est là pour toi !"),
    1: ("Hackeur Débrouillard <i class='bi bi-lightning'></i>", "Tu trouves des solutions malgré les contraintes. L'esprit dev camerounais est en toi. Continue à itérer !"),
    2: ("Pionnier du Code <i class='bi bi-rocket-takeoff'></i>", "Tu transformes chaque obstacle en opportunité. Ton état d'esprit est celui des grands créateurs. Le Cameroun a besoin de toi !"),
    3: ("Légende du Game Dev Cam <i class='bi bi-trophy'></i>", "Ton niveau de résilience est exceptionnel. Tu es exactement le profil qui va révolutionner le jeu vidéo camerounais. La voie est tracée !"),
}

SCORES_CHOIX = {
    "A": 0, "B": 1, "C": 2  # scenario 3 : B=1 ou C=2 → on garde la logique simple
}

# Pour le scénario 3 uniquement, B et C valent 1 point chacun (=résilience)
def calc_score(c1, c2, c3):
    s = 0
    s += 1 if c1 == "C" else 0
    s += 1 if c2 == "C" else 0
    s += 1 if c3 in ("B", "C") else 0
    return s


# ─── Routes ──────────────────────────────────────────────────────────────────

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        aide = request.form.getlist('aide_souhaitee')
        r = Reponse(
            age=request.form.get('age'),
            ville=request.form.get('ville'),
            statut=request.form.get('statut'),
            connexion=request.form.get('connexion'),
            tentative_game=request.form.get('tentative_game'),
            moteur=request.form.get('moteur'),
            apprentissage=request.form.get('apprentissage'),
            publie=request.form.get('publie'),
            score_frein_materiel=int(request.form.get('frein_materiel', 1)),
            score_frein_connexion=int(request.form.get('frein_connexion', 1)),
            score_frein_formation=int(request.form.get('frein_formation', 1)),
            score_frein_monetisation=int(request.form.get('frein_monetisation', 1)),
            score_frein_familial=int(request.form.get('frein_familial', 1)),
            aide_souhaitee=', '.join(aide),
            theme_reve=request.form.get('theme_reve'),
        )
        db.session.add(r)
        db.session.commit()

        # Notification Telegram
        msg = (
            f"<b>Nouvelle reponse CamGame Pulse !</b>\n"
            f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"<b>Profil</b>\n"
            f"  - Age : {r.age}\n"
            f"  - Ville : {r.ville}\n"
            f"  - Statut : {r.statut}\n"
            f"  - Connexion : {r.connexion}\n\n"
            f"<b>Pratique</b>\n"
            f"  - Tentative jeu : {r.tentative_game}\n"
            f"  - Moteur : {r.moteur}\n"
            f"  - Apprentissage : {r.apprentissage}\n"
            f"  - Publie : {r.publie}\n\n"
            f"<b>Freins (1-5)</b>\n"
            f"  - Materiel : {r.score_frein_materiel}\n"
            f"  - Connexion : {r.score_frein_connexion}\n"
            f"  - Formation : {r.score_frein_formation}\n"
            f"  - Monetisation : {r.score_frein_monetisation}\n"
            f"  - Familial : {r.score_frein_familial}\n\n"
            f"<b>Aide souhaitee</b> : {r.aide_souhaitee or '-'}\n"
            f"<b>Jeu reve</b> : {r.theme_reve or '-'}\n"
            f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"ID #{r.id}"
        )
        send_telegram(msg)

        return redirect(url_for('main.minigame', user_id=r.id))
    return render_template('index.html')


@bp.route('/minigame/<int:user_id>', methods=['GET'])
def minigame(user_id):
    r = Reponse.query.get_or_404(user_id)
    return render_template('minigame.html', user_id=user_id, scenarios=SCENARIOS)


@bp.route('/minigame/<int:user_id>/submit', methods=['POST'])
def minigame_submit(user_id):
    data = request.get_json()
    c1 = data.get('s1', 'A')
    c2 = data.get('s2', 'A')
    c3 = data.get('s3', 'A')
    score = calc_score(c1, c2, c3)
    titre, texte = DIAGNOSTICS[score]
    diagnostic = f"{titre}|{texte}"

    mg = Minigame(
        session_id=user_id,
        scenario1_choix=c1,
        scenario2_choix=c2,
        scenario3_choix=c3,
        score_resilience=score,
        diagnostic=diagnostic,
    )
    db.session.add(mg)
    db.session.commit()
    return jsonify({"score": score, "titre": titre, "texte": texte})


@bp.route('/merci/<int:user_id>')
def merci(user_id):
    r = Reponse.query.get_or_404(user_id)
    mg = r.minigame
    score = mg.score_resilience if mg else 0
    titre, texte = DIAGNOSTICS.get(score, DIAGNOSTICS[0])
    return render_template('merci.html', score=score, titre=titre, texte=texte)


@bp.route('/dashboard')
def dashboard():
    reponses = Reponse.query.all()
    # Villes
    villes = {}
    for r in reponses:
        if r.ville:
            villes[r.ville] = villes.get(r.ville, 0) + 1

    # Freins moyens
    freins = {
        "Matériel": 0, "Connexion": 0, "Formation": 0,
        "Monétisation": 0, "Famille": 0
    }
    n = len(reponses) or 1
    for r in reponses:
        freins["Matériel"] += r.score_frein_materiel or 0
        freins["Connexion"] += r.score_frein_connexion or 0
        freins["Formation"] += r.score_frein_formation or 0
        freins["Monétisation"] += r.score_frein_monetisation or 0
        freins["Famille"] += r.score_frein_familial or 0
    freins = {k: round(v / n, 1) for k, v in freins.items()}

    # Moteurs
    moteurs = {}
    for r in reponses:
        if r.moteur:
            moteurs[r.moteur] = moteurs.get(r.moteur, 0) + 1

    # Score résilience moyen
    mgs = Minigame.query.all()
    score_moy = round(sum(m.score_resilience or 0 for m in mgs) / (len(mgs) or 1), 1)

    # Thèmes de rêve (nuage de mots simplifié)
    themes_raw = [r.theme_reve for r in reponses if r.theme_reve]

    return render_template('dashboard.html',
        total=len(reponses),
        villes=json.dumps(villes),
        freins=json.dumps(freins),
        moteurs=json.dumps(moteurs),
        score_moy=score_moy,
        themes=json.dumps(themes_raw),
    )


@bp.route('/export')
def export():
    reponses = Reponse.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id','age','ville','statut','connexion','tentative_game','moteur',
        'apprentissage','publie','frein_materiel','frein_connexion',
        'frein_formation','frein_monetisation','frein_familial',
        'aide_souhaitee','theme_reve',
        'mg_s1','mg_s2','mg_s3','score_resilience','diagnostic'
    ])
    for r in reponses:
        mg = r.minigame
        writer.writerow([
            r.id, r.age, r.ville, r.statut, r.connexion, r.tentative_game,
            r.moteur, r.apprentissage, r.publie,
            r.score_frein_materiel, r.score_frein_connexion,
            r.score_frein_formation, r.score_frein_monetisation, r.score_frein_familial,
            r.aide_souhaitee, r.theme_reve,
            mg.scenario1_choix if mg else '', mg.scenario2_choix if mg else '',
            mg.scenario3_choix if mg else '', mg.score_resilience if mg else '',
            mg.diagnostic if mg else '',
        ])
    output.seek(0)
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=camgame_pulse_data.csv'}
    )
