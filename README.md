# Discord - NFT Sales Bot  
A discord bot that post NFT sales on OpenSea to a discord channel.

**How it works**  
Every minute the bot will call Opensea for any new sales. If sales are found the bot will post them to the channel the setup.
The bot will post sales from oldest to newst each run. If there are no sales not thing is posted. 


# Setup Guide  

## Create Your Bot - Discord Setup Guide  
https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot


## Discord Server Token  
1. In discord, click the gear icon next to your username
1. Select Advanced from the left nav menu
1. Trun on developer mode
1. Go to the server you want to add the bot to
1. Click the down arrow next to the Server's name
1. Select Server Settings -> Widget
1. Copy the Server ID
1. Copy the Channel ID
1. Update setting bot.config file.


## The bot.config file  
1. Set the Discord API_TOKEN
1. Set the Discord Channel ID where the bot should post sales
1. Set the Contract Address
1. Set the Opensea API Key
1. Set the Opensea Collection Slug


## Bot Server Setup  
Install pip
`sudo apt install python3-pip`

Install discord.py
`python3 -m pip install -U discord.py`

Install discord_slash.py
`sudo -H pip3 install -U discord-py-slash-command`

`sudo -H pip3 install python-dateutil`


## Starting the bot  
1. Open a command window at the root on the app
1. Run `python3 main.py` to start the bot
1. Crtl+C to stop the bot.


**Running the bot as a background service**  
Review Service.md
