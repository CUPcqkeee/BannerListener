import os
import disnake
from disnake.ext import commands

bot = commands.Bot(
    command_prefix="a.",
    intents=disnake.Intents.all(),
    case_insensitive=True,
    help_command=None,
    allowed_mentions=disnake.AllowedMentions.all())

path = "./cogs"
for root, dirs, files in os.walk(path):
    for filename in files:
        if filename.endswith(".py"):
            cog_path = os.path.relpath(os.path.join(root, filename), path)
            module = os.path.splitext(cog_path)[0].replace(os.sep, '.')
            bot.load_extension(f"cogs.{module}")

token = open("token.txt", "r").readline()

bot.run(token)
