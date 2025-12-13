from typing import Optional
import os
import sys
import random
import discord
from click import pass_context
from discord import app_commands, VoiceClient
from dotenv import load_dotenv
import requests
import asyncio
import psutil
from datetime import datetime
from discord.utils import get
from gpio import cleanup
import pyttsx3
# import ollama
import re
import pandas as pd
import datetime
import base64
import json
from PIL import Image




#edits the settings of the bot for the respective guild
#takes the guild id and the channel id of the gamba, minecraft and tts channels
def settingsSetter(guild_id, gambaChannel=None, minecraftChannel=None, ttsChannel=None):
    response = ""
    client_settings = pd.read_csv("userSettings.csv")
    if client_settings.loc[client_settings["guildID"] == guild_id].empty:
        new_row = {"guildID": str(guild_id), "gambaChannel": str(gambaChannel), "minecraftChannel": str(minecraftChannel), "ttsChannel": str(ttsChannel)}
        client_settings.loc[len(client_settings)] = new_row
        client_settings.to_csv("userSettings.csv", index=False)
        response = f"settings created for guild id: {guild_id}"
    else:
        if gambaChannel is not None:
            client_settings.loc[client_settings["guildID"] == guild_id, "gambaChannel"] = str(gambaChannel)
            response = f"{response} gamba channel set to <#{gambaChannel}>,"
        if minecraftChannel is not None:
            client_settings.loc[client_settings["guildID"] == guild_id, "minecraftChannel"] = str(minecraftChannel)
            response = f"{response} minecraft channel set to <#{minecraftChannel}>,"
        if ttsChannel is not None:
            client_settings.loc[client_settings["guildID"] == guild_id, "ttsChannel"] = str(ttsChannel)
            response = f"{response} tts channel set to <#{ttsChannel}>"
        if response == "":
            response = "no settings changed"
        client_settings.to_csv("userSettings.csv", index=False)
    client_settings = None
    return response
#checks if the channel in the guild is allowed to have bot messages
def check_channel(guild_id, channel_id, message_author, gamba=False, minecraft=False, tts=False):
    is_allowed = False
    client_settings = pd.read_csv("userSettings.csv", dtype={"guildID": str, "gambaChannel": str, "minecraftChannel": str, "ttsChannel": str})
    client_guild = client_settings.loc[client_settings["guildID"] == str(guild_id)]
    print(f"checking settings for: {guild_id} channel: {channel_id}")
    if client_guild.empty:
        print("not client guild")
        return False       
    else:
        if gamba:
            if str(channel_id) in str(client_guild["gambaChannel"].values):
                is_allowed = True
            else:
                print("set channel: " + str(client_guild["gambaChannel"].values))
                is_allowed = False
        elif minecraft:
            if str(channel_id) in client_guild["minecraftChannel"].values:
                is_allowed = True
            else:
                print("set channels: " + str(client_guild["minecraftChannel"].values))
                is_allowed = False
        elif tts:
            if str(channel_id) in str(client_guild["ttsChannel"].values):
                is_allowed = True
            else:
                is_allowed = False
        else:
            is_allowed = True
        client_settings = None
        return is_allowed
#writes the message and server sent from to the file and logs how many times some commands were used
def write_file(user, message, server="DM", command="none"):
    #writes the message data to the file

    with open('Logs.txt', 'a') as logs:
        logs.write(f"\n{datetime.datetime.now()} Server: {server} message: {user}: {command}")
    #checks for command usage and increments the respective number
    if command == "none":
        #if a command isn't inputted it won't be counted towards anything
        return
    else:
        try:
            with open("Logs.txt", 'r') as file:
                data = file.readlines()
            command_amount = int(data[data.index(f"{command}\n") +1]) +1   
            data[data.index(f"{command}\n") +1] = str(f"{command_amount}\n")
            with open('Logs.txt', 'w') as file:
                file.writelines(data)
        except ValueError:
            return


#adds an event to Events.txt
def create_event(event, date):
    with open('Events.txt', 'a') as events:
        events.write(f"{event}: {date} \n")
#deletes an event from Events.txt
def del_event(event):
    with open('Events.txt', 'r') as events:
        data = events.readlines()
    del data[event - 1]
    with open("Events.txt", 'w') as events:
        events.writelines(data)
#reads all events in Events.txt
def read_events():   
    final_read = ""
    with open('Events.txt', 'r') as events:
        data = events.readlines()
    for x in range(len(data)):
        data_storage = data[x]
        final_read += f"{x + 1}. {data_storage}"
    return final_read



#checks is user is available in GambaLogs.txt
def check_user(author_id):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if f"{author_id}\n" in data:
        return True
    else:
        return False
#generates a random number and return a random item from ITEMS for slots
def Sspin():
    randomNumber = random.randint(0, 5)
    return ITEMS[randomNumber]
#gets the results of the slots spin
def Sget_results(wheels):
    if (wheels[0] == "CHERRY") and (wheels[1] != "CHERRY"):
        return 6
    elif (wheels[0] == "CHERRY") and (wheels[1] == "CHERRY") and (wheels[2] != "CHERRY"):
        return 9
    elif (wheels[0] == "CHERRY") and (wheels[1] == "CHERRY") and (wheels[2] == "CHERRY"):
        return 11
    elif (wheels[0] == "ORANGE") and (wheels[1] == "ORANGE") and (wheels[2] == "ORANGE"):
        return 14
    elif (wheels[0] == "PLUM") and (wheels[1] == "PLUM") and (wheels[2] == "PLUM"):
        return 18
    elif (wheels[0] == "BELL") and (wheels[1] == "BELL") and (wheels[2] == "BELL"):
        return 24
    elif (wheels[0] == "BAR") and (wheels[1] == "BAR") and (wheels[2] == "BAR"):
        return 254
    else:
        return 0
#creates an account within the GambaLogs.txt
def create_account(author, author_id):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if  f"{author_id}\n" not in data:
        data.append(f"user:\n{author}\nuserID:\n{author_id}\nmoney:\n1000\n")
        with open("GambaLogs.txt", 'w') as file:
            file.writelines(data)
        return True
    else:
        return False
#returns the amount of money in the respective accounts
def get_money(author_id):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if  f"{author_id}\n" in data:
        money = int(data[data.index(f"{author_id}\n") + 2])
        return money, True
    else:
        return 
#removes a specified amount of money from respective account
def remove_money(author_id, amount):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if f"{author_id}\n" in data:
        money_index = data.index(f"{author_id}\n") + 2
        after_money = int(data[money_index]) - amount
        data[money_index] = str(f"{after_money}\n")
        with open("GambaLogs.txt", 'w') as file:
            file.writelines(data)
#adds a specified amount of money to respective account
def add_money(author_id, amount):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if f"{author_id}\n" in data:
        money_index = data.index(f"{author_id}\n") + 2
        after_money = int(data[money_index]) + amount
        data[money_index] = str(f"{after_money}\n")
        with open("GambaLogs.txt", 'w') as file:
            file.writelines(data)
#retruns the full results of each spin and calls add and subtract money functions
def slots_spin(spins, author_id):
    with open("GambaLogs.txt", 'r') as file:
        data = file.readlines()
    if f"{author_id}\n" in data and get_money(author_id)[0] >= 3 * spins:
        spin_total = 0
        spin_resultsSTR = ""
        cost = 3 * spins
        remove_money(author_id, cost)
        spin_results = [[Sspin() for x in range(0, 3)] for j in range(0, spins)]

        for x in spin_results:
            spin_total += Sget_results(x)
            spin_resultsSTR += f"{x[0]} | {x[1]} | {x[2]} payout: {Sget_results(x)}\n"
        add_money(author_id, spin_total)
        return [spin_resultsSTR, spin_total]
    else:
        return ["None", "None"]

def slots_calculations(spins, message_authorID):
    if spins > 100:
        spins = 100
    if spins <= 0:
        spins = 1
    slots_resultsTULP = slots_spin(spins, message_authorID)
    if slots_resultsTULP[0] != 'None':
        return [slots_resultsTULP[0], slots_resultsTULP[1], -(spins * 3) + slots_resultsTULP[1]]
    else:
        return

async def MC_Server_Proccess(interaction: discord.Interaction):
    """Subprocess running the minecraft server"""
    global output
    global server_process
    startup_script_path = os.getenv('STARTUP_PATH')
    global server_process
    if server_process and server_process.returncode is None:
            await interaction.response.send_message("Oi! The server is already running or is having a critical error. Check Minecraft first, then contact the owner.")
            print("message responded") 
    else:
        # Start the process
        server_process = await asyncio.create_subprocess_exec(
            "bash", startup_script_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await interaction.response.send_message("Server starting up. Please wait a moment.")

        # Read stdout and stderr asynchronously
        async for line in server_process.stdout:
            print(f"STDOUT: {line.decode().strip()}")
            output = line

        async for line in server_process.stderr:
            print(f"STDERR: {line.decode().strip()}")
    print("message responded")


babyYoda_memes = ["https://cdn.discordapp.com/attachments/1162221035505066084/1162223866609946664/IMG_1700.jpg?ex=653b2852&is=6528b352&hm=398ddc74ec70b33e270e55fbd7e3f5cc228b8fbab21c789fed61cc1749f6f52c&", "https://cdn.discordapp.com/attachments/1162221035505066084/1162223866257604669/IMG_1701.jpg?ex=653b2852&is=6528b352&hm=92f956ff09b973ad16096ee234ca251a99efa7350ec655c316dffbe6f3e4be7e&", "https://cdn.discordapp.com/attachments/1162221035505066084/1162223504574402570/IMG_4378.jpg?ex=653b27fc&is=6528b2fc&hm=882fac6f1c1dc1704a26a1eabaaf5f9380712dc6a6ed510edd75a583ee8024d7&", "https://images.squarespace-cdn.com/content/v1/52df0e63e4b07360a57e5bb8/1575836269357-3JO98844S7S7U6Z05XLE/Baby+Yoda+Work+.png?format=1500w", "https://hips.hearstapps.com/hmg-prod/images/baby-yoda-pope-1574183303.jpeg?crop=1xw:0.7398452611218569xh;center,top&resize=1200:*", "https://pbs.twimg.com/media/Enuta6UVEAAE4WD?format=jpg&name=900x900", "https://wkml.com/wp-content/uploads/sites/53/2019/12/Baby-Yoda-Memes-4-297x300.jpg", ]
slots_payTable = 'BAR\tBAR\tBAR\t\tpays\t$254\nBELL\tBELL\tBELL\tpays\t$24\nPLUM\tPLUM\tPLUM\tpays\t$18\nORANGE\tORANGE\tORANGE\tpays\t$14\nCHERRY\tCHERRY\tCHERRY\t\tpays\t$11\nCHERRY\tCHERRY\t  -\t\tpays\t$9\nCHERRY\t  -\t  -\t\tpays\t$6'
ITEMS = ["CHERRY", "LEMON", "ORANGE", "PLUM", "BELL", "BAR"]

server_process = None
output = None
global voice_channel
voice_channel = None
joinee = None
engine = pyttsx3.init()
global client_settings
# ollama.pull("deepseek-r1:7b")


#bot start up process
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} has connected to Discord!')
    try: 
        synced = await tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

@tree.command(name="settings")
@app_commands.describe(gamba_channel="channel for gamba commands", minecraft_channel="channel for minecraft commands", tts_channel="channel for text to speech")
async def settings(interaction: discord.Interaction, 
                   gamba_channel: discord.TextChannel = None, 
                   minecraft_channel: Optional[discord.TextChannel] = None, 
                   tts_channel: Optional[discord.TextChannel] = None):
    """sets the channels for gamba, minecraft and tts"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.")
        return
    guild_id = interaction.guild.id
    gamba_id = gamba_channel.id if gamba_channel else None
    minecraft_id = minecraft_channel.id if minecraft_channel else None
    tts_id = tts_channel.id if tts_channel else None
    responce = settingsSetter(guild_id, gamba_id, minecraft_id, tts_id)
    await interaction.response.send_message(responce)

@tree.command(name="online")
async def online(interaction: discord.Interaction):
    """Checks the online status of the Minecraft server and returns the list of online players."""
    startup_script_path = os.getenv('STARTUP_PATH')
    server_config_path = startup_script_path.replace("Startup.sh", "server.properties")
    if check_channel(interaction.guild.id, interaction.channel.id, interaction.user, minecraft=True):
        write_file(interaction.user, '/online', interaction.guild, '/online')
        Emoji_guild = client.get_guild(938325287333154896)
        if server_process and server_process.returncode is None:
            global output
            server_process.stdin.write(f"list\n".encode())
            await server_process.stdin.drain()
            await asyncio.sleep(1)
            output = re.sub(r'\x1b\[[0-9;]*m', '', output.decode().strip())
            if len(output.split("players online: ")) < 2:
                await interaction.response.send_message("The server is running but no players are online.")
                return
            number_of_players = output.split("There are ")[1].split(" of a max")[0].strip()
            players = output.split("players online: ")[1].strip().split(", ")
            client_emojis = Emoji_guild.emojis
            for player in players:
                    if player in [emoji.name for emoji in client_emojis]:
                        player_emoji = discord.utils.get(client_emojis, name=player)
                        players[players.index(player)] = f"{player_emoji}{player}"
                    else:
                        player_uuid = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}").json()["id"]
                        player_value = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}").json()["properties"][0]["value"]
                        player_texture = json.loads(base64.b64decode(player_value))["textures"]["SKIN"]["url"]
                        with open(f"skin.png", "wb") as image_file:
                            image_file.write(requests.get(player_texture).content)
                        image_file = Image.open("skin.png")
                        image_file.crop((8, 8, 16, 16)).save("skin.png")
                        image_file.close()
                        image_file = Image.open("skin.png")
                        image_file.resize((128, 128), resample=Image.NEAREST).save(f"{player}.png")
                        image_file.close()
                        await Emoji_guild.create_custom_emoji(name=player, image= open(f"{player}.png", "rb").read())
                        player_emoji = discord.utils.get(client_emojis, name=player)
                        players[players.index(player)] = f"{player_emoji}{player}"
            thumbnail_url = "https://i.ibb.co/gbXqwpq9/image.png"
            motd = ""
            with open(server_config_path, 'r') as file:
                data = file.readlines()
                for line in data:
                    if "motd=" in line:
                        motd = line.strip().split("motd=")[1]
                        break
                    else:
                        motd = "No MOTD available"
            embed_description = motd
            online_embed = discord.Embed(title="Server Status", color=discord.Color.green(), description=embed_description)
            online_embed.set_thumbnail(url=thumbnail_url)
            online_embed.add_field(name="Online Players", value=str(number_of_players), inline=True)
            online_embed.add_field(name="Players", value='\n'.join(players) if players else "No players online", inline=True)
            await interaction.response.send_message(embed=online_embed)
        else:
            await interaction.response.send_message("The server is not running.")
        print("message responded")

@tree.command(name="start")
async def start(interaction: discord.Interaction):
    """Starts the Minecraft server."""
    if check_channel(interaction.guild.id, interaction.channel.id, interaction.user, minecraft=True):
        write_file(interaction.user, 'SLASH COMMAND', interaction.guild, '/start')
        await MC_Server_Proccess(interaction)
        

@tree.command(name="command")
async def slash(interaction: discord.Interaction, command: str):
    """Sends a command to the Minecraft server console."""
    global output
    if check_channel(interaction.guild.id, interaction.channel.id, interaction.user, minecraft=True):         
            write_file(interaction.user, 'SLASH COMMAND', interaction.guild, f'/{command}')
            if server_process and server_process.returncode is None:
                server_process.stdin.write(f"{command}\n".encode())
                await server_process.stdin.drain()
                await interaction.response.send_message(f"Server Response: {output.decode().strip()}")
            else:
                await interaction.response.send_message("The server is not running. Cannot send command.")
            print("message responded")

@tree.command(name="ip")
async def ip(interaction: discord.Interaction):
    """Checks the IP address of the Minecraft server."""
    server_ip = os.getenv('Server_IP')
    if check_channel(interaction.guild.id, interaction.channel.id, interaction.user, minecraft=True):         
            write_file(interaction.user, 'SLASH COMMAND', interaction.guild, '/ip')
            await interaction.response.send_message(f"The server IP address is: ||{server_ip}||")
            print("message responded")

#shash command for gambling and responds with the message authors money stored in GambaLogs.txt
@tree.command(name="money")
async def money(interaction: discord.Interaction):
    """Checks the amount of money in the user's account."""
    message_author = interaction.user
    if check_channel(interaction.guild.id, interaction.channel.id, message_author, gamba=True):         
            write_file(message_author, "SLASH COMMAND", interaction.guild, "/money")
            if get_money(message_author.id)[1]:
                await interaction.response.send_message(f"{message_author}`s money is ${get_money(message_author.id)[0]}")
            else:
                await interaction.response.send_message(f"either an error occurred or user {message_author} doesnt exists")
            print("message responded")

@client.event
async def on_voice_state_update(member, before, after):
    global joinee
    global voice_channel
    if joinee is not None: 
        if member == joinee and after.channel is not before.channel:
            await vc.disconnect(force=True)
            cleanup()
            voice_channel = None
            joinee = None



#reading messages and respond
@client.event
async def on_message(message):
    global server_process
    
    #checks if the message is from the bot
    if message.author == client.user:
        return
    #gets message content
    if message.author != client.user:
        print("message read")
        msg = message.content.lower()
        RAW_MSG = message.content
        user = discord.utils.get(client.guilds[0].members, id=message.author.id)
        message_author = message.author
        message_authorID = message.author.id
        #gets guild information
        if str(message.guild) != 'None': 
            channel_id = str(message.channel.id)
            guild_id = str(message.guild.id)
            guild_name = str(message.guild)
        print(f"{message_author}: {RAW_MSG}, channel id: {channel_id}")
        
    #checks message content for the word cat and gives a random image of a cat                     
    if msg == "cat":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            cat_request = requests.get("https://api.thecatapi.com/v1/images/search").json()
            cat = cat_request[0]
            cat = cat["url"]
            await message.channel.send(cat)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            cat_request = requests.get("https://api.thecatapi.com/v1/images/search").json()
            cat = cat_request[0]
            cat = cat["url"]
            await message.channel.send(cat)
            print("message responded")
        else:
            return
    
    #checks message content for the word cat and gives a random image of a dog
    if msg == "dog":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            dog_request = requests.get("https://dog.ceo/api/breeds/image/random").json()
            dog = dog_request["message"]
            await message.channel.send(dog)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            dog_request = requests.get("https://dog.ceo/api/breeds/image/random").json()
            dog = dog_request["message"]
            await message.channel.send(dog)
            print("message responded")
        else:
            return
            
    #checks message content for the word duck and gives a random image of a duck
    if msg == "duck":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            duck_request = requests.get("https://random-d.uk/api/v2/random").json()
            duck = duck_request["url"]
            await message.channel.send(duck)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, msg, guild_name, msg)
            duck_request = requests.get("https://random-d.uk/api/v2/random").json()
            duck = duck_request["url"]
            await message.channel.send(duck)
            print("message responded")
        else:
            return

    #checks message content for the word joke and gives a random dad joke
    if msg == "joke":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            joke_request = requests.get("https://icanhazdadjoke.com/slack").json()
            joke = (joke_request["attachments"][0])
            joke = joke["text"]
            await message.channel.send(joke)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name,msg)
            joke_request = requests.get("https://icanhazdadjoke.com/slack").json()
            joke = (joke_request["attachments"][0])
            joke = joke["text"]
            await message.channel.send(joke)
            print("message responded")
        else:
            return

    #checks message content for the words baby yoda and gives a random baby yoda meme (NOT USING API)
    if msg == "baby yoda":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            random_number = random.randint(0, len(babyYoda_memes) - 1)
            random_image = babyYoda_memes[random_number]
            await message.channel.send(random_image)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            random_number = random.randint(0, len(babyYoda_memes) - 1)
            random_image = babyYoda_memes[random_number]
            await message.channel.send(random_image)
            print("message responded")
        else:
            return

    #checks message content for the words !arrest and shuts down all programs running greq
    if msg == "!arrest" and message_authorID == 851651703413669938:
        await message.channel.send("Rats!, foiled again.")
        sys.exit(1)
    
    #events section
    #checks for a messages that starts with !addevent and looks for an event name and date if there is no date detected it will send an error message
    if msg.startswith('!addevent'):
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            res = msg.split()
            event = ""
            for i in range(1, len(res)):
                if res[i] == "date":
                    break
                event += res[i] + " "
            event = event.strip()
            res = msg.split("date ", 1)
            if len(res) > 1:
                dateAndTime = res[1]
                create_event(event, dateAndTime)
                await message.channel.send(f"event created: {event}")
                print("message responded")
            else:
                await message.channel.send(f"it seems you entered the command wrong !help for more commands")
            
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            res = msg.split()
            event = ""
            for i in range(1, len(res)):
                if res[i] == "date":
                    break
                event += res[i] + " "
            event = event.strip()
            res = msg.split("date ", 1)
            if len(res) > 1:
                dateAndTime = res[1]
                create_event(event, dateAndTime)
                await message.channel.send(f"event created: {event}")
                print("message responded")
            else:
                await message.channel.send(f"it seems you entered the command wrong !help for more commands")
                print("message responded")
        else:
            return
    #checks message content for the words !events and gives the list of events
    if msg == "!events":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            await message.channel.send(read_events())
            print("message responded")           
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            await message.channel.send(read_events())
            print("message responded")
        else:
            return
    #checks message content for the words !delevent and a number to delete the corresponding event
    if msg.startswith("!delevent"):
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            res = msg.split()
            event_index = int(res[1])
            if event_index >= 1:
                del_event(event_index)
                await message.channel.send(f"event {event_index} deleted")
            print("message responded")           
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            res = msg.split()
            event_index = int(res[1])
            if event_index >= 1:
                del_event(event_index)
                await message.channel.send(f"event {event_index} deleted")
            print("message responded")
        else:
            return
    
    #checks message content for the words !help and responds with the contents of the commands file
    if msg == "!help":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            commands_help = ""
            with open('Commands.txt', 'r')as file:             
                 data = file.readlines()
            for x in data:
                commands_help += x
            await message.channel.send(commands_help)
            print("message responded")           
        elif check_channel(guild_id, channel_id, message_author):
            write_file(message_author, RAW_MSG, guild_name, msg)
            commands_help = ""
            with open('Commands.txt', 'r')as file:             
                 data = file.readlines()
            for x in data:
                commands_help += x
            await message.channel.send(commands_help)
            print("message responded")
        else:
            return
    
    #gamba section
    #checks message content for the words !gamba and responds with the contents of the GambaCommands file
    if msg == "!gamba":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            commands_gamba = ""
            with open("GambaCommands.txt", 'r')as file:
                data = file.readlines()
            for x in data:
                commands_gamba += x
            await message.channel.send(commands_gamba)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author, True):
            write_file(message_author, RAW_MSG, command=msg)
            with open("GambaCommands.txt", 'r')as file:
                data = file.readlines()
            commands_gamba = ""
            with open("GambaCommands.txt", 'r')as file:
                data = file.readlines()
            for x in data:
                commands_gamba += x
            await message.channel.send(commands_gamba)
            print("message responded")

     #checks message content for the words !addaccount and adds account to logs

    #checks message content for the words !addaccount and adds message authors account to GambaLogs.txt
    if msg == "!addaccount":
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            if create_account(message_author, message_authorID):
                await message.channel.send(f"{message_author}'s account has been created and starts with $1000")
            else:
                await message.channel.send(f"either an error occurred or user {message_author} already exists")
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author, True):
            write_file(message_author, RAW_MSG, guild_name, msg)
            if create_account(message_author, message_authorID):
                await message.channel.send(f"{message_author}'s account has been created and starts with $1000")
            else:
                await message.channel.send(f"either an error occurred or user {message_author} already exists")
            print("message responded")

    #cheakc message content for the words !slotspt and responds with the slots pay table
    if msg.startswith("!slotspt"):
        if str(message.guild) == 'None':
            write_file(message_author, RAW_MSG, command=msg)
            await message.channel.send(slots_payTable)
            print("message responded")
        elif check_channel(guild_id, channel_id, message_author, True):
            write_file(message_author, RAW_MSG, guild_name, msg)
            await message.channel.send(slots_payTable)
            print("message responded")

    #checks message content for !slots and will run slots() function
    elif msg.startswith("!slots"):
        if check_user(message_authorID):
            if str(message.guild) == 'None':
                write_file(message_author, RAW_MSG, command=msg)
                spins = 1
                try:
                    spins = int(msg.split()[1])
                    results = slots_calculations(spins, message_authorID)
                    await message.channel.send(f"total winnings: {results[1]}\n money: {get_money(message_authorID)[0]} ({results[2]})")
                    print("message responded")
                except IndexError:
                    results = slots_calculations(spins, message_authorID)
                    await message.channel.send(f"total winnings: {results[1]}\n money: {get_money(message_authorID)[0]} ({results[2]})")
                    print("message responded")
            elif check_channel(guild_id, channel_id, message_author, True):
                write_file(message_author, RAW_MSG, command=msg)
                spins = 1
                try:
                    spins = int(msg.split()[1])
                    results = slots_calculations(spins, message_authorID)
                    await message.channel.send(f"total winnings: {results[1]}\n money: {get_money(message_authorID)[0]} ({results[2]})")
                    print("message responded")
                except IndexError:
                    results = slots_calculations(spins, message_authorID)
                    await message.channel.send(f"total winnings: {results[1]}\n money: {get_money(message_authorID)[0]} ({results[2]})")
                    print("message responded")
        else:
            return

    #end of gamba section


    if msg == "give verify":
        role = get(message.guild.roles, name='Verified')
        await message.author.add_roles(role)
        await message.channel.send("problem solved?")
        print("message responded")

    #text to speech section
    if msg == "!join":
        if str(message.guild) == "None":
            write_file(message_author, RAW_MSG, command=msg)
            await message.channel.send('command unavalible')
        elif check_channel(guild_id, channel_id, message_author, minecraft=True):
            global vc
            global joinee
            global voice_channel
            write_file(message_author, RAW_MSG, command=msg)
            if message_author.voice is None:
                await message.channel.send("you need to be in a vc")
            else:
                voice_channel = message_author.voice.channel
                joinee = message_author
                vc = await voice_channel.connect()
                print(f" vc id: {voice_channel.id}")
    if voice_channel is not None and channel_id == str(voice_channel.id):
        if len(msg) < 500:
            msg.replace("sabrin", "suhbreen")
            engine.save_to_file(f"{message_author} says {msg}", "Voice.mp3")
            engine.runAndWait()
            vc.play(discord.FFmpegPCMAudio("Voice.mp3"))
            engine.stop()
        else:
            engine.save_to_file("fuck you", "Voice.mp3")
            engine.runAndWait()
            vc.play(discord.FFmpegPCMAudio("Voice.mp3"))
            engine.stop()
    
    # if msg.startswith("<@1149848512469676082>"):
    #     if str(message.guild) == 'None':
    #         write_file(message_author, RAW_MSG, command=msg)
    #         await message.channel.send("Feature not supported here")
    #         print("Message responded")           
    #     elif check_channel(guild_id, channel_id, message_author, gamba=True):
    #         write_file(message_author, RAW_MSG, guild_name, msg)
    #         GREQ = "your name is greq also known in computer language as <@1149848512469676082>. you do you best to only respong within 600 characters now you are amaericas most wanted, banned from walmarts across the U.S for building forts in the shelves. you are trapped in a dsicord server full of people who warship you but you like to banter and be insulting in the funniest way possible, remember you are a criminal on the run" 
    #         response = ollama.chat(model='deepseek-r1:7b', messages=[
    #             {
    #                 'role': 'user',
    #                 'content': f'respond within 600 characters please this is your prompt: {msg}'    
    #             }
    #         ])
    #         greqResponce = response['message']['content']
    #         greqResponceFormatted = re.sub(r"<think>.*?</think>", "", greqResponce, flags=re.DOTALL)
    #         print(greqResponceFormatted)
    #         await message.channel.send(greqResponceFormatted)
    #         print("Message responded")

client.run(TOKEN)