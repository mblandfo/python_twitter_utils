import twitter
import load_passwords
import load_settings
import csv
import os.path
import sys
import pytz
from datetime import datetime, timedelta
from util import *

# https://github.com/bear/python-twitter

# https://python-twitter.readthedocs.io/en/latest/

config = load_passwords.load()
settings = load_settings.load()

api = twitter.Api(consumer_key=config["consumer_key"],
                  consumer_secret=config["consumer_secret"],
                  access_token_key=config["access_token_key"],
                  access_token_secret=config["access_token_secret"],
                  sleep_on_rate_limit=True,
                  tweet_mode="extended")

# Note: for a list of timezones, look at pytz.common_timezones
timezone = pytz.timezone(settings["timezone"])

tweetsOutputFileName = 'hashtag_tweets.csv'
startDateString = "2019-05-15"
# endDateString = "2019-06-17"

start = parseDate(startDateString)
# end = parseDate(endDateString) + timedelta(days=1)

apiDateFormat = "%Y-%m-%d"
twitterDateFormat = "%a %b %d %H:%M:%S %z %Y"

hashtags = [
    '#ibiza',
    '#ibizagate',
    '#ibizavideo',
    '#ibizaaffaere',
    '#HCStrache',
    '#Strache',
    '#StracheVideo',
    '#StracheGate',
    '#Kurz',
    '#FPÖ',
    '#fpoe',
    '#Bierlein',
    '#übergangsregierung',
    '#neuwahlen',
    '#neuwahl',
    '#philippastrache',
    '#Kickl',
    '#Regierungskrise',
    '#Misstrauensantrag',
    '#Misstrauensvotum',
]

def write_tweets_for_tag(tag):
    search_query = 'q=' + hash_tag
    search_query = search_query.replace('#', '%23') 
    search_query += '&result_type=recent'
    search_query += '&since=' + startDateString
    search_query += '&count=100'

    tweets = get_all_for_query(search_query)
    return tweets

def write_all_for_query(query):
    earliestTweet = None
    max_id = None

    while(True):
        raw_query = query + '&count=100'
        if max_id is not None:
            raw_query += '&max_id=' + str(max_id)
        newTweets = api.GetSearch(raw_query=raw_query)
        if not newTweets:
            return
        for tweet in newTweets:
            tweet.created_at_date = parseTwitterDate(tweet.created_at)
        earliestTweet = min(newTweets, key=lambda x: x.created_at_date)
        earliestTweetDate = earliestTweet.created_at_date
        print(printDateOnly(earliestTweetDate), end=' ', flush=True)
        write_tweets_to_file(newTweets)
        max_id = earliestTweet.id

        if earliestTweetDate < start or len(newTweets) == 1:
            return


def write_tweets_any_hashtag():
    sep = '%20OR%20'
    search_query = 'q=' + sep.join(hashtags)
    search_query = search_query.replace('#', '%23')
    search_query += '&result_type=recent'
    search_query += '&since=' + startDateString

    tweets = write_all_for_query(search_query)
    return tweets

def write_tweets_to_file(tweets):
    with open(tweetsOutputFileName, 'a', newline='', encoding='utf-8') as csvfile:
        csvWriter = csv.writer(csvfile)        
        csvWriter.writerow(["screen_name", "tweet_id", "created_at", "text"])
        for tweet in tweets:
            screen_name = tweet.user.screen_name
            created_at_date = datetime.fromtimestamp(tweet.created_at_in_seconds)
            row = [
                screen_name,
                tweet.id, 
                printDate(created_at_date), 
                tweet.full_text or tweet.text
            ]
            csvWriter.writerow(row)

if os.path.exists(tweetsOutputFileName):
    os.remove(tweetsOutputFileName)

write_tweets_any_hashtag()

