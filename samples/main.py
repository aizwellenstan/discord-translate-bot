import os
import requests
import emoji
import csv
import discord
from keep_alive import keep_alive
from discord.ext import commands
from datetime import datetime, timedelta
from googletrans import Translator
from secret import TOKEN

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(
    intents=intents,
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True  # Commands aren't case-sensitive
)

bot.author_id = "377094288485646338"  # Discord ID of the bot author
translator = Translator()

# Log file for testing purposes
def log(user, server, channel, source_lang, target_lang, translateMe, result):
    with open('./log.csv', 'a', encoding='UTF8', newline='') as f:
        now = datetime.now() - timedelta(hours=5)
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        row = [
            now, user, server, channel, source_lang, target_lang, translateMe,
            result
        ]
        writer = csv.writer(f)
        writer.writerow(row)


@bot.event
async def on_ready():  # When the bot is ready
    print("Bot connected!")
    print(bot.user)  # Prints the bot's username and ID
    print("Serving ", sum(len(g.members) for g in bot.guilds),
          " users, across ", len(bot.guilds), " servers")


@bot.command(name="translate", aliases=["tl"])
async def translate(ctx, *args):
    '''Translates between EN, JA, and ZH-TW.
        Reply to a message you wish to translate with: !translate
        Or, enter: !translate [Sentence to be translated]'''

    channel = ctx.channel.name
    server = ctx.guild.name
    user = ctx.author

    translateMe = " ".join(args).strip()

    if not translateMe:  # If no args, get the msg this command replied to
        if ctx.message.reference:
            translateMe = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            translateMe = translateMe.content
        else:
            await ctx.reply("No text provided for translation.")
            return

    print("Translation request: ", translateMe)

    if emoji.demojize(translateMe).isascii():  # If text is EN
        source_lang = 'en'
        target_langs = ['ja', 'zh-tw']
    elif any('\u4e00' <= ch <= '\u9fff' for ch in translateMe):  # If text is ZH-TW
        source_lang = 'zh-tw'
        target_langs = ['en', 'ja']
    else:  # Assume text is JA
        source_lang = 'ja'
        target_langs = ['en', 'zh-tw']
    
    results = []
    
    for target_lang in target_langs:
        try:
            result = translator.translate(translateMe, src=source_lang, dest=target_lang).text
            results.append(f"**{target_lang.upper()}:** {result}")
            log(user, server, channel, source_lang, target_lang, translateMe, result)
        except Exception as e:
            errMsg = f"Translation to {target_lang} failed. Error: {e}"
            print("Error: ", errMsg)
            results.append(errMsg)
            log(user, server, channel, source_lang, target_lang, translateMe, errMsg)
    
    await ctx.reply("\n".join(results))

keep_alive()  # Starts a webserver to be pinged.
# token = os.environ['DISCORD_BOT_SECRET']  # Discord bot token: Discord dev portal -> Your Bot -> Token
token = TOKEN
try:
    bot.run(token)  # Starts the bot
except Exception as e:
    print("Bot unable to start")
    print(e.__class__)
    print(getattr(e, 'status', 'No status'))
    print(getattr(e, 'response', 'No response'))
    if getattr(e, 'status', None) == 429:
        print("Rate Limited, Unable to start")
    print(e)
