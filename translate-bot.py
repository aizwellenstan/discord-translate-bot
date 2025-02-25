import os
import requests
import emoji
import csv
import discord
from keep_alive import keep_alive
from datetime import datetime, timedelta
from googletrans import Translator
import re
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
    # Prevent the bot from responding to itself
    if message.author == bot.user:
        return
    
    content = message.content.strip()
    if not content:
        return
    
    channel = message.channel.name
    server = message.guild.name if message.guild else "DM"
    user = message.author.name
    
    target_langs = ['ja', 'zh-tw', 'en']
    
    # Check if the bot is mentioned in the message
    if bot.user.mentioned_in(message):
        # Remove the bot's mention from the content (regex will match the bot's mention pattern)
        content_without_mention = re.sub(r"<@!?(\d+)>", "", content).strip()  # Remove bot mention
        
        # Create a thread from the message and send reply in it
        if message.channel.type == discord.ChannelType.text:
            try:
                # Use the original message content (without mention) as the thread's name
                thread_name = content_without_mention[:100]  # Limit to 100 characters (Discord's limit for thread names)
                
                # Create a thread from the original message
                """
                60: 1 hour
                1440: 1 day (24 hours)
                4320: 3 days
                10080: 7 days
                """
                thread = await message.create_thread(name=thread_name, auto_archive_duration=40320)
                
                # Send the translated response in the newly created thread
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

                # Reply in the created thread
                if results:
                    await thread.send(content="\n".join(results))
                await message.reply(f"Thread created: {thread.mention}")
            except discord.Forbidden:
                await message.reply("I do not have permission to create threads in this channel.")
            return
    else:
        # Continue with translation (this part is unchanged) if bot is not mentioned
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
            # If it's in a thread, reply in the thread
            if message.thread:
                await message.thread.send(content="\n".join(results))
            # else:
            #     # Otherwise, reply in the main channel
            #     await message.reply(content="\n".join(results))

keep_alive()
try:
    bot.run(TOKEN)
except Exception as e:
    print("Bot unable to start")
    print(e.__class__, getattr(e, 'status', 'No status'), getattr(e, 'response', 'No response'))
    if getattr(e, 'status', None) == 429:
        print("Rate Limited, Unable to start")
    print(e)
