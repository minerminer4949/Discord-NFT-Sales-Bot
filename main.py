# coding=UTF-8

import logging
import logging.handlers as handlers
import requests
import configparser
import datetime
from dateutil import parser
import discord
from discord.ext.commands.bot import Bot
from discord import Embed
from discord.colour import Color
from discord.ext import tasks
from discord_slash import SlashCommand, SlashContext

CONFIG_FILE = "bot.config" #"/usr/bin/py-scripts/py-sales-bot/bot.config"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
DISCORD_API_TOKEN=config.get("DISCORD","API_TOKEN")
OS_COLLECTION_NAME=config.get("OPENSEA","COLLECTION_NAME")
OS_API_KEY=config.get("OPENSEA","API_KEY")
headers = {'X-API-KEY': OS_API_KEY}

#now we will Create and configure logger
logger=logging.getLogger()
logger.setLevel(logging.INFO)

# config the file
formatter = logging.Formatter('%(asctime)s - %(levelname)s: - %(message)s')
logHandler = handlers.TimedRotatingFileHandler('py-sales-bot.log', when='D', interval=1, backupCount=2)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


my_intents = discord.Intents.default()
my_intents.members = True
bot = Bot('/', intents=my_intents)
slash = SlashCommand(bot)  

class MyClient(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__('/',*args, **kwargs)
        self.IS_START_UP=True
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        self.CONTRACT_ADDRESS=config.get('CONTRACT','ADDRESS')
        self.discord_channel_id=int(config.get('DISCORD','CHANNEL_ID'))   
        self.OS_COLLECTION_NAME=config.get("OPENSEA","COLLECTION_NAME")
        self.OS_API_KEY=config.get("OPENSEA","API_KEY")
        self.last_sale_timestamp="2022-03-31T00:00:00Z"
        self.show_hodler_status = True

        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------ Sales Bot started ------')
        logging.info("Sales Bot started")

    @tasks.loop(seconds=60) # task runs every 60 seconds
    async def my_background_task(self):
        try:
            if(self.IS_START_UP == False):
                logging.info("Sales activity check started.")
                events_url = "https://api.opensea.io/api/v1/events?only_opensea=false&asset_contract_address=" + str(self.CONTRACT_ADDRESS) + "&event_type=successful&occurred_after=" + str(self.last_sale_timestamp)
                #print (events_url)
                events_response = requests.get(events_url, headers=headers)
                json_data = events_response.json()
                temp_event_list = []
                for event_temp in json_data["asset_events"]:
                    temp_event_list.insert(0, event_temp)

                for asset_event in temp_event_list:
                    #print("Asset event")
                    # Get the json data.
                    token_id = asset_event.get("asset").get("token_id")
                    image_url=asset_event.get("asset").get("image_preview_url")
                    asset_name=asset_event.get("asset").get("name")
                    total_price = asset_event.get("total_price")
                    seller_name = asset_event.get("seller").get("user").get("username")
                    seller_address = asset_event.get("seller").get("address")
                    winner_address = asset_event.get("winner_account").get("address")
                    winner_name = winner_address[0:6]

                    # format the sales price
                    formatted_value="0.0"
                    value_temp=str(total_price)
                    if(len(value_temp) > 18):
                        formatted_value = (value_temp[:(len(value_temp) - 18)] + "." + value_temp[(len(value_temp) - 18):])[:5]
                    else:
                        formatted_value = ("0." + str(value_temp).rjust(18, '0'))[:5]

                    # Add 1 second to the last sale timestamp.
                    formatted_value = formatted_value + " ⧫"
                    self.last_sale_timestamp=asset_event.get("transaction").get("timestamp")
                    parsed_time=parser.parse(self.last_sale_timestamp)
                    added_seconds = datetime.timedelta(0, 1)
                    self.last_sale_timestamp = ((parsed_time + added_seconds).isoformat())[:19] + "Z"
                    # Format the discord post.
                    embed=Embed(title=asset_name, type="rich",url="https://opensea.io/assets/" + str(self.CONTRACT_ADDRESS) + "/" + str(token_id), color = Color.green(), description="has just been sold for " + str(formatted_value) + " \n")
                    embed.set_thumbnail(url=image_url)  
                    embed.add_field(name="**From**", value="[" + str(seller_name) + "](https://opensea.io/" + str(seller_address) + ")", inline="true")
                    embed.add_field(name="**To**", value="[" + str(winner_name) + "](https://opensea.io/" + str(winner_address) + ")" , inline="true")
                    channel = self.get_channel(self.discord_channel_id) # channel ID goes here
                    embed.set_footer(text="Data provided by OpenSea", icon_url="https://storage.googleapis.com/opensea-static/Logomark/Logomark-Blue.png")
                    #await self.change_presence(activity=discord.Game(name="a game"))
                    await channel.send(embed=embed)
        except Exception as e:
            logging.error("Get bot sales failed. " + str(e))

        if( self.IS_START_UP == True):
            # This is the first run. Get the last sale timestamp
            logging.info("This is the first run. Get the last sale timestamp.")
            self.IS_START_UP = False
            data_url = "https://api.opensea.io/api/v1/events?only_opensea=false&asset_contract_address=" + str(self.CONTRACT_ADDRESS) + "&event_type=successful&occurred_after=" + str(self.last_sale_timestamp)
            startup_response = requests.get(data_url,headers=headers)
            startup_data = startup_response.json()
            self.last_sale_timestamp=startup_data["asset_events"][0].get("transaction").get("timestamp")
            parsed_time=parser.parse(self.last_sale_timestamp)
            added_seconds = datetime.timedelta(0, 0)
            self.last_sale_timestamp = ((parsed_time + added_seconds).isoformat())[:19] + "Z"
            logging.info("Start up - last sale time stamp " + self.last_sale_timestamp)
            print("Start up - last sale time stamp " + self.last_sale_timestamp)

        try:
            #print("inside try catch")
            stats_data_url = "https://api.opensea.io/api/v1/collection/" + str(self.OS_COLLECTION_NAME) + "/stats"
            stats_data_response = requests.get(stats_data_url,headers=headers)
            stats_data_json = stats_data_response.json()
            stats_data = stats_data_json["stats"]
            num_owners = stats_data.get("num_owners")
            floor_price = stats_data.get("floor_price")
            if (self.show_hodler_status == True):
                self.show_hodler_status = False
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= str(num_owners) + " hodlers"))
            else:
                self.show_hodler_status = True
                formatted_value="0.0"
                if isinstance(floor_price, float):
                    formatted_value = str(round(floor_price, 3))
                else:
                    formatted_value = str(floor_price)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Floor: " + str(floor_price)))
        except Exception as e:
            logging.error("Update bot status failed. " + str(e))


    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() # wait until the bot logs in

client = MyClient()
client.run(DISCORD_API_TOKEN)

