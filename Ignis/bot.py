import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # Adicione o GUILD_ID no arquivo .env

# Configuração de intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True

# Inicialização do bot
class IgnisBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.log_channel_id = None

    async def setup_hook(self):
        # Sincronizar comandos apenas no servidor especificado
        guild = discord.Object(id=GUILD_ID)
        try:
            await self.tree.sync(guild=guild)
            print(f"Comandos sincronizados com o servidor {GUILD_ID}.")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")

client = IgnisBot()