import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# =========================
# SERVEUR POUR RENDER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Apple of Fortune Bot is running!")

    def log_message(self, format, *args):
        return


def start_server():
    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(f"Serveur actif sur le port {port}")

    server.serve_forever()


# =========================
# ANALYSE DES RESULTATS
# =========================

def analyser(resultats):

    valeurs = []

    for resultat in resultats:

        try:
            valeur = resultat.lower().replace("x", "").strip()
            valeurs.append(float(valeur))

        except ValueError:
            continue

    if not valeurs:
        return (
            "❌ Je n'ai trouvé aucun résultat valide.\n\n"
            "Exemple :\n"
            "1.20x 1.50x 2.00x 3.00x"
        )

    moyenne = sum(valeurs) / len(valeurs)

    moins_de_2 = sum(
        1 for valeur in valeurs
        if valeur < 2
    )

    plus_de_2 = sum(
        1 for valeur in valeurs
        if valeur >= 2
    )

    maximum = max(valeurs)
    minimum = min(valeurs)

    if moyenne < 1.5:
        tendance = "FAIBLE 🔴"

    elif moyenne < 2.5:
        tendance = "MOYENNE 🟡"

    else:
        tendance = "ÉLEVÉE 🟢"

    return (
        "🍎 APPLE OF FORTUNE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"📊 Résultats analysés : {len(valeurs)}\n\n"

        f"📈 Moyenne : {moyenne:.2f}x\n"

        f"🔽 Moins de 2x : {moins_de_2}\n"

        f"🔼 2x ou plus : {plus_de_2}\n\n"

        f"⬇️ Minimum : {minimum:.2f}x\n"

        f"⬆️ Maximum : {maximum:.2f}x\n\n"

        f"🎯 Tendance : {tendance}\n\n"

        "⚠️ IMPORTANT\n"
        "Cette analyse utilise uniquement les résultats "
        "que tu fournis. Elle ne peut pas garantir le "
        "prochain résultat du jeu."
    )


# =========================
# COMMANDE /START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "🍎 BIENVENUE SUR APPLE OF FORTUNE BOT !\n\n"

        "🤖 Je peux analyser une série de résultats "
        "et calculer des statistiques.\n\n"

        "📌 Envoie plusieurs résultats séparés par "
        "des espaces.\n\n"

        "Exemple :\n"
        "1.20x 1.50x 2.00x 1.10x 3.00x\n\n"

        "⚠️ Je ne peux pas garantir le prochain résultat."
    )

    await update.message.reply_text(message)


# =========================
# RECEPTION DES RESULTATS
# =========================

async def recevoir_resultats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    texte = update.message.text

    resultats = texte.split()

    resultat = analyser(resultats)

    await update.message.reply_text(resultat)


# =========================
# PROGRAMME PRINCIPAL
# =========================

def main():

    token = os.environ.get("BOT_TOKEN")

    if not token:

        raise ValueError(
            "❌ BOT_TOKEN n'est pas configuré dans Render."
        )

    # Démarrer le serveur Render
    serveur = threading.Thread(
        target=start_server,
        daemon=True
    )

    serveur.start()

    # Créer le bot Telegram
    application = (
        Application.builder()
        .token(token)
        .build()
    )

    # Commande /start
    application.add_handler(
        CommandHandler("start", start)
    )

    # Messages contenant les résultats
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            recevoir_resultats
        )
    )

    print("🍎 Apple of Fortune Bot démarré !")

    # Démarrer Telegram
    application.run_polling()


# =========================
# LANCEMENT
# =========================

if __name__ == "__main__":
    main()
