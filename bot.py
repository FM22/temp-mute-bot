import discord
import os
import dotenv
import asyncio

# get secret token from .env file
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

timeDict = {'s': 1, 'm': 60, 'h': 3600}

# would really love to avoid having to do this
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print("Connected")
    await client.change_presence(activity = discord.Game(name=";help"))

@client.event
async def on_message(message):
    author = message.author
    channel = message.channel

    # help command
    if not (author.bot or author.system) and message.content == ';help':
        await author.send("Bot help:\n**;mute [time][s/m/h]**\nMutes you for a specified amount of time.\nOnly works in the work channel.\n\n**;blind [time][s/m/h]**\nBlinds you for a specified amount of time.\nOnly works in the work channel.\n\n**;unmute [@user1] [@user2] ...**\nUnmutes and unblinds specified users.\nAdmin-only.")
        return

    # other commands
    if type(channel).__name__ == "TextChannel" and channel.name == "im-gonna-do-a-question-for-an-hour" and not (author.bot or author.system) and type(author).__name__ == "Member":
        text = message.content
        if text[0] == ";":
            #get role to add
            roleDict = {"mute": discord.utils.get(message.guild.roles, name="muted"), "blind": discord.utils.get(message.guild.roles, name="blind")}
            msgDict = {"mute": "muted", "blind": "blinded"}
            words = text[1:].split(" ")

            # mute/blind command
            if words[0] in roleDict.keys():
                newRole = roleDict[words[0]]
                base = words[1][:-1]
                if base.isdigit():
                    multi = words[1][-1]
                    timeout = timeDict.get(multi, 60) * int(base)
                    await author.add_roles(newRole)
                    await channel.send(msgDict[words[0]].title() + " " + author.name + " for " + str(int(base)) + (multi if multi in timeDict.keys() else 'm'))
                    await asyncio.sleep(timeout)
                    if newRole in discord.utils.get(client.get_all_members(), id = author.id).roles:
                        await author.remove_roles(newRole)
                        await channel.send(author.name + " is back!")
                return

            # "save me" command
            if words[0] == "clear":
                if author.permissions_in(channel).administrator:
                    savedUsers = message.mentions
                    for u in savedUsers:
                        await u.remove_roles(roleDict["mute"])
                        await u.remove_roles(roleDict["blind"])
                    await channel.send(author.name + " force cleared " + "".join([(u.name + ", ") for u in savedUsers[:-1]]) + (" and " if len(savedUsers) > 1 else "") + savedUsers[-1].name)
                else:
                    await author.send("Get an admin to do this :slight_smile:")
                return
client.run(TOKEN)