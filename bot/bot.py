import disnake
import sqlite3
import requests
from disnake.ext import commands
from src.utils.logger import logger

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all(), command_sync_flags=commands.CommandSyncFlags.all())

conn = sqlite3.connect("user_keys.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS user_keys (
    user_id INTEGER PRIMARY KEY,
    key TEXT NOT NULL
)''')
conn.commit()

def save_key(user_id: int, key: str):
    c.execute("REPLACE INTO user_keys (user_id, key) VALUES (?, ?)", (user_id, key))
    conn.commit()

def get_key(user_id: int):
    c.execute("SELECT key FROM user_keys WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    return result[0] if result else None

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("------")

@bot.slash_command(name="add")
async def add(interaction: disnake.AppCmdInter):
    pass

@add.sub_command(name="key", description="Link your API key to your user")
async def addkey(interaction: disnake.AppCmdInter, key: str):
    user_id = interaction.user.id
    save_key(user_id, key)
    await interaction.response.send_message("Your key has been saved successfully.", ephemeral=True)

@bot.slash_command(name="balance", description="Check your balance")
async def balance(interaction: disnake.AppCmdInter, key: str = None):
    user_id = interaction.user.id
    final_key = key or get_key(user_id)

    if not final_key:
        await interaction.response.send_message(
            "No key provided and none saved. Use `/addkey` to store your key.",
            ephemeral=True
        )
        return

    try:
        r = requests.get("https://api.captchasolver.ai/api/getBalance", params={"key": final_key}, timeout=5)
        data = r.json()
        await interaction.response.send_message(
            f"Your balance is: {data['balance']} credits",
            ephemeral=True
        )
    except requests.RequestException as e:
        logger.error(f"Error fetching balance: {str(e)}")
        await interaction.response.send_message(
            f"Error fetching balance: {str(e)}",
            ephemeral=True
        )

@bot.slash_command(name="status", description="Check the solver status")
async def status(interaction: disnake.AppCmdInter):
    online = True
    try:
        requests.get("https://api.captchasolver.ai/api/status", timeout=5)
    except:
        online = False

    await interaction.response.send_message(
        f"Solver is {'online' if online else 'offline'}",
    )

@bot.event
async def on_message(message: disnake.Message):
    if message.mentions and bot.user in message.mentions:
        await message.channel.send("Hai :3")

@bot.event
async def on_guild_join(guild: disnake.Guild):
    logger.info(f"was added guild: {guild.name} (ID: {guild.id})")
    await guild.leave()

bot.run("MTI0MzU3MjE0ODI3MDc5Mjc1NA.G74mZw.sAPZLwNKiiEHZE1JUm5LyPQsvNR25VmdP2MlWg")
