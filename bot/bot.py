import discord
from discord.ext import tasks
import os
from TwitterAPI import TwitterAPI
from datetime import datetime
import requests
import json
import os.path

class Bot(discord.Client):
    
    def __init__(self):
        super().__init__()
        self.version = "2021.35a"
        
        self.twitter_api = self.init_twitter_api()
        self.twitter_user_id = "1356336382722138113" # https://twitter.com/Onura_tv
        self.twitter_user = self.get_twitter_user_by_id(self.twitter_user_id)
        self.news_text_channel_id = 807778867719962654
        self.twitter_last_tweet_in_text_channel = datetime.now() # Should be no problem for now. But it doesn't take care about tweets that got posted in the bot downtime.
        self.twitch_user_id = "644758191" # https://twitch.tv/onuratv
        
    async def on_ready(self):
        activity = discord.Game(f"ver. {self.version}")
        await self.change_presence(status=discord.Status.online, activity=activity)
        if not os.path.isfile('data.json'):
            with open('data.json', 'w') as json_file:
                data = {"twitter_last_tweet_in_text_channel": str(datetime.now())}
                json.dump(data, json_file)
                self.twitter_last_tweet_in_text_channel = datetime.now()
        else:
            with open('data.json') as json_file:
                data = json.load(json_file)
                self.twitter_last_tweet_in_text_channel = datetime.fromisoformat(data['twitter_last_tweet_in_text_channel'])

        self.update_loop.start()
        print("[ONURABOT] Bot started.")
        
    async def on_message(self, message):
        pass

    def init_twitter_api(self):
        consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")

        api = TwitterAPI(consumer_key, consumer_secret, auth_type="oAuth2", api_version='2')

        return api

    def get_twitter_user_by_id(self, twitter_id):
        result = self.twitter_api.request(f'users/:{twitter_id}')

        return list(result)[0]

    @tasks.loop(seconds=60)
    async def update_loop(self):
        result = self.twitter_api.request(f"users/:{self.twitter_user_id}/tweets", {"max_results": 5, "tweet.fields": "created_at"})
        for tweet in reversed(list(result)):
            str_tweet_time = tweet['created_at']          # example result: 2021-08-26T21:23:41.000Z
            str_tweet_time = str_tweet_time.split('.')[0] # only use the part before '.', so it is recognized as an iso format

            tweet_time = datetime.fromisoformat(str_tweet_time)
            if tweet_time > self.twitter_last_tweet_in_text_channel:
                self.twitter_last_tweet_in_text_channel = tweet_time
                await self.get_channel(self.news_text_channel_id).send(f"https://twitter.com/{self.twitter_user['username']}/status/{tweet['id']}")
                with open('data.json', 'w') as json_file:
                    data = {"twitter_last_tweet_in_text_channel": str(tweet_time)}
                    json.dump(data, json_file)

        is_live = self.check_if_live_on_twitch()
        if is_live:
            await self.get_channel(self.news_text_channel_id).send("@everyone JETZT LIVE! https://twitch.tv/onuratv")


    def check_if_live_on_twitch(self):
        twitch_access_token = os.getenv("TWITCH_ACCESS_TOKEN")
        twitch_client_id = os.getenv("TWITCH_CLIENT_ID")

        headers = {
            'Authorization': f'Bearer {twitch_access_token}',
            'Client-Id': twitch_client_id
        }

        r = requests.get(f'https://api.twitch.tv/helix/users?id={self.twitch_user_id}', headers=headers)
        data = r.json()
        data = data['data'][0]
        if data['type'] == 'live': return True
        else: return False
        
