import discord
import os
import dotenv
import asyncio

# get secret token from .env file
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

timeDict = {'s': 1, 'm': 60, 'h': 3600}
bound_channels = {"im-gonna-do-a-question-for-an-hour", "spam"}
admin_roles = {"super admin", "artem", "nice person"}
msgDict = {"mute": "muted", "blind": "blinded"}
admin_commands = {"admin": admin_roles, "channel": bound_channels}
admin_commands_txt = {"admin": "as an admin role", "channel": "as a bound channel"}


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
    is_admin = intersection(set([r.name for r in author.roles]), admin_roles) or author.permissions_in(channel).administrator

    # help command
    if not (author.bot or author.system) and message.content == ';help':
        await author.send("""
        *User Commands (only work in work/spam channels):*\n
        **;mute [time][s/m/h]**\n
        Mutes you for a specified amount of time.\n
        Only works in the work channel.\n\n
        **;blind [time][s/m/h]**\n
        Blinds you for a specified amount of time.\n
        Only works in the work channel.\n\n
        *Admin only commands:*\n
        **;clear [@user1] [@user2] ...**\n
        Unmutes and unblinds specified users.\n\n
        **;admin [add/remove] [role]**\n
        Adds or removes the specified role as an admin role for this bot.\n\n
        **;channel [add/remove] [channel name]**\n
        Adds or removes the specified channel as a usable channel for the mute and blind commands.""")
        return

    # other commands
    if type(channel).__name__ == "TextChannel" and type(author).__name__ == "Member" and (channel.name in bound_channels or is_admin) and not (author.bot or author.system):
        text = message.content
        if text[0] == ";":
            #get role to add
            roleDict = {"mute": discord.utils.get(message.guild.roles, name="muted"), "blind": discord.utils.get(message.guild.roles, name="blind")}
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

            # admin-only commands
            if is_admin:
                if words[0] == "clear":
                        savedUsers = message.mentions
                        for u in savedUsers:
                            await u.remove_roles(roleDict["mute"])
                            await u.remove_roles(roleDict["blind"])
                        await channel.send(author.name + " force cleared " + "".join([(u.name + ", ") for u in savedUsers[:-1]]) + (" and " if len(savedUsers) > 1 else "") + savedUsers[-1].name)
                        return

                if words[0] in admin_commands.keys():
                    arg = words[2]
                    if words[1] == "add":
                        admin_commands[words[0]].add(words[2])
                        await channel.send("Added " + words[2] + " " + admin_commands_txt[words[0]])
                    elif words[1] == "remove":
                        admin_commands[words[0]].remove(words[2])
                        await channel.send("Removed " + words[2] + " " + admin_commands_txt[words[0]])
            else:
                await author.send("Get an admin to do this :slight_smile:")

client.run(TOKEN)