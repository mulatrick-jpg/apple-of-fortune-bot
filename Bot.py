import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

def analyser(resultats):
    valeurs = []
    for r in resultats:
        try:
            valeurs.append(float(r.replace("x", "").strip()))
        except ValueError:
            pass

    if not valeurs:
        return "❌ Je n'ai pas trouvé de résultats valides."

    moyenne = sum(valeurs) / len(valeurs)
    petits = sum(1 for x in valeurs if x < 2)
    grands = sum(1 for x in valeurs if x >= 2)

    if moyenne < 1.5:
        tendance = "faible"
    elif moyenne < 2.5:
        tendance = "moyenne"
    else:
        tendance = "élevée"

    return (
        f"🍎 ANALYSE APPLE OF FORTUNE\n\n"
        f"📊 Résultats analysés : {len(valeurs)}\n"
        f"📈 Moyenne : {moyenne:.2f}x\n"
        f"🔽 Résultats < 2x : {petits}\n"
        f"🔼 Résultats ≥ 2x : {grands}\n"
        f"🎯 Tendance statistique : {tendance}\n\n"
        f"⚠️ Cette analyse ne garantit pas le prochain résultat."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍎 Bienvenue sur Apple of Fortune Bot !\n\n"
        "Envoie-moi plusieurs résultats séparés par des espaces.\n\n"
        "Exemple :\n"
        "1.20x 2.10x 1.50x 3.00x 1.10x"
    )

async def recevoir_resultats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = update.message.text
    resultats = texte.split()
    await update.message.reply_text(analyser(resultats))

def main():
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN n'est pas configuré.")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_resultats)
    )

    application.run_polling()

if __name__ == "__main__":
    main()
