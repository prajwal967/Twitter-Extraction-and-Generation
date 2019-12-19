import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from configparser import ConfigParser

class Authenticate():
    
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(self.auth)

class TwitterListener(StreamListener):
    
    def __init__(self, filename):
        self.filename = filename
        
    def on_data(self, data):
        try:
            with open(self.filename, 'a') as file:
                file.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print(status)
        return True

if __name__ == "__main__":
    
    conf = ConfigParser()
    conf.read("config/keys.ini")

    consumer_key = conf.get('keys', 'consumer_key')
    consumer_secret = conf.get('keys', 'consumer_secret')
    access_token = conf.get('keys', 'access_token')
    access_secret = conf.get('keys', 'access_secret')
    
    authenticate = Authenticate(consumer_key, consumer_secret, access_token, access_secret)
    twitter_listener = TwitterListener('euro_python.json')
    
    twitter_stream = Stream(authenticate.auth, twitter_listener)
    #Looking for the tweets to scrape, will scrape tweets with '#europython','#EuroPython'
    twitter_stream.filter(track=['#europython','#EuroPython'])