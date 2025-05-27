import os
from dotenv import load_dotenv
from bot import client  # Importa o client do bot.py
from commands import add, remove, leaderboard, set_log_channel, vc_log
from events import on_ready, on_member_join

# Carregar variáveis do arquivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Inicialização do bot
if __name__ == "__main__":
    client.run(TOKEN)