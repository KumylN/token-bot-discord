# bot.py
import os
import json
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

def id_to_member(id):
    id = id[3:-1]
    member = None
    for m in client.guilds[0].members:
        if m.id == int(id):
            member = m.name
            break
    return member

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    is_commands = message.channel.name == 'commands'
    if message.content.startswith('Hello token bot') and is_commands:
        channel = message.channel
        await channel.send('Hello {}, I am token bot'.format(message.author.name))

    elif message.content.startswith('give') and is_commands:
        message_split = message.content.split()
        channel = message.channel
        if len(message_split) == 3:
            current_tokens = None
            amount = message_split[1]
            member = id_to_member(message_split[2])
            with open('tokens.json', 'r') as f:
                current_tokens = json.loads(f.read())
            
            if current_tokens is not None and member and int(amount) > 0:
                if member not in current_tokens:
                    current_tokens[member] = {
                        message.author.name: amount,
                    }
                else:
                    if message.author.name not in current_tokens[member]:
                        current_tokens[member][message.author.name] = amount
                    else:
                        current_tokens[member][message.author.name] = str(int(current_tokens[member][message.author.name]) + int(amount))

                await channel.send('{} now has {} tokens from {}'.format(member, current_tokens[member][message.author.name], message.author.name))
                with open('tokens.json', 'w') as f:
                    f.write(json.dumps(current_tokens))
        else:
            await channel.send('Unrecognized command, format is \'give <amount> <member name>\''.format(message.author.name))
    elif message.content.startswith('check') and is_commands:
        channel = message.channel
        message_split = message.content.split()
        if len(message_split) == 2:
            member = id_to_member(message_split[1])
            if member:
                with open('tokens.json', 'r') as f:
                    current_tokens = json.loads(f.read())
                
                if current_tokens is not None:
                    count = 0
                    if member in current_tokens and message.author.name in current_tokens[member]:
                       count = current_tokens[member][message.author.name]
                    else:
                        count = 0 
                    await channel.send('{} has {} tokens from you'.format(member, count))
        elif len(message_split) == 1:
            std_out = 'You have the following tokens: \n\n'
            with open('tokens.json', 'r') as f:
                current_tokens = json.loads(f.read())
             
            if message.author.name in current_tokens:
                count = 0
                for member in current_tokens[message.author.name]:
                    std_out+= '{}: {}\n'.format(member, current_tokens[message.author.name][member])
                    count += int(current_tokens[message.author.name][member])
                
                if count == 0:
                    std_out = 'You have no tokens!'
            else:
                std_out = 'You have no tokens!'
            
            await channel.send(std_out)
    elif message.content.startswith('use') and is_commands:
        channel = message.channel
        message_split = message.content.split()
        # use <amount> <member>
        if len(message_split) == 3:
            amount = message_split[1]
            member = id_to_member(message_split[2])
            with open('tokens.json', 'r') as f:
                current_tokens = json.loads(f.read())
            
            if message.author.name in current_tokens and member in current_tokens[message.author.name] and current_tokens[message.author.name][member] >= int(amount):
                current_tokens[message.author.name][member] = str(int(current_tokens[message.author.name][member]) - int(amount))
                with open('tokens.json', 'w') as f:
                    f.write(json.dumps(current_tokens))
                std_out = 'You now have {} tokens for {}'.format(current_tokens[message.author.name][member], member)
            else:
                std_out = 'You do not have enough tokens to do that for {}'.format(member)
            
            await channel.send(std_out)

client.run(TOKEN)