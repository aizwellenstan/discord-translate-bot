import os
import requests
import emoji
import csv
import discord
from keep_alive import keep_alive
from datetime import datetime, timedelta
from googletrans import Translator
from secret import TOKEN

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

bot = discord.Client(intents=intents)
translator = Translator()

def log(user, server, channel, target_lang, translateMe, result):
    with open('./log.csv', 'a', encoding='UTF8', newline='') as f:
        now = datetime.now() - timedelta(hours=5)
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        row = [now, user, server, channel, target_lang, translateMe, result]
        writer = csv.writer(f)
        writer.writerow(row)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Serving", sum(len(g.members) for g in bot.guilds), "users, across", len(bot.guilds), "servers")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    content = message.content.strip()
    if not content:
        return
    
    channel = message.channel.name
    server = message.guild.name if message.guild else "DM"
    user = message.author.name
    
    target_langs = ['ja', 'zh-tw', 'en']

    results = []
    for target_lang in target_langs:
        try:
            result = await translator.translate(content, dest=target_lang)
            result_text = result.text  # Extract translated text
            results.append(f"**{target_lang.upper()}:** {result_text}")
            log(user, server, channel, target_lang, content, result_text)
        except Exception as e:
            errMsg = f"Translation to {target_lang} failed. Error: {e}"
            print("Error:", errMsg)
            results.append(errMsg)
            log(user, server, channel, target_lang, content, errMsg)
    
    if results:
        # Edit the original message with the translated results
        await message.edit(content="\n".join(results))

keep_alive()
try:
    bot.run(TOKEN)
except Exception as e:
    print("Bot unable to start")
    print(e.__class__, getattr(e, 'status', 'No status'), getattr(e, 'response', 'No response'))
    if getattr(e, 'status', None) == 429:
        print("Rate Limited, Unable to start")
    print(e)
