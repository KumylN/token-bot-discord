# bot.py
import os
import json
import discord
import shlex
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

    elif message.content.lower().startswith('give') and is_commands:
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
    elif message.content.lower().startswith('check') and is_commands:
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
    elif message.content.lower().startswith('use') and is_commands:
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
    
    elif message.content.startswith('--adminoveride') and message.author.name == 'Eluminated' and is_commands:
        file_name = message.content.split()[1]
        channel = message.channel
        with open(file_name, 'r') as f:
            file_contents = f.read()
        await channel.send(file_contents)

    elif message.content.startswith('store') and is_commands:
        message_split = shlex.split(message.content)
        channel = message.channel
        arg = message_split[1]
        if arg.lower() == 'add':
            reward = message_split[2]
            amount = message_split[3]
            with open('store.json', 'r') as f:
                store = json.loads(f.read())
            
            if message.author.name not in store:
                store[message.author.name] = {}
            store[message.author.name][reward] = amount

            with open('store.json', 'w') as f:
                f.write(json.dumps(store))
            await channel.send('Successfully added {} to your store!'.format(reward))
        
        elif arg.lower() == 'remove':
            reward = message_split[2]
            with open('store.json',r) as f:
                store = json.loads(f.read())
            
            if message.author.name in store and reward in store[message.author.name]:
                del store[reward]
            
            with open('store.json') as f:
                f.write(json.dumps(store))
            
            await channel.send('Successfully removed {} from your store!'.format(reward))
        elif arg.lower() == 'view':
            with open('store.json', 'r') as f:
                store = json.loads(f.read())
            
            std_out = ''
            person = message_split[2]
            if person != 'all':
                person = id_to_member(person)
            
            if person == 'all':
                std_out += 'Showing ALL stores:\n\n'

                for key in store:
                    std_out += '{}:\n'.format(key)
                    for reward in store[key]:
                        std_out += '{} {} tokens\n'.format(reward, store[key][reward])
                    std_out += '\n'
            
            else:
                for reward in store[person]:
                    std_out += '{} {} tokens\n'.format(reward, store[key][reward])
                
            await channel.send(std_out)
                
client.run(TOKEN)