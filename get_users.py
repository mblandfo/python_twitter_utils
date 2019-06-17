import twitter
import load_passwords
import load_settings
import csv
import os.path
import sys
import pytz
from datetime import datetime, timedelta
import util

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

inputFileName = settings["inputFileName"]
userOutputFileName = settings["userOutputFileName"]
tweetsOutputFileName = settings["tweetsOutputFileName"]
startDateString = settings["startDateString"]
endDateString = settings["endDateString"]
# Note: for a list of timezones, look at pytz.common_timezones
timezone = pytz.timezone(settings["timezone"])

apiDateFormat = "%Y-%m-%d"
twitterDateFormat = "%a %b %d %H:%M:%S %z %Y"

screen_names = []

if not os.path.isfile(inputFileName):
    print("Input file not found: " + inputFileName)
    sys.exit()

with open(inputFileName, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        screen_names.append(row[0])
    print("Loaded " + str(len(screen_names)) +
          " twitter screen names from " + inputFileName)

usersLoaded = []

# Note: api.GetSearch only gets very recent data, so doing this complicated workaround instead


def getTweets(user, startDateString, endDateString):
    screen_name = user.screen_name
    tweets = []
    start = parseDate(startDateString)
    end = parseDate(endDateString) + timedelta(days=1)

    earliestTweet = None
    max_id = None
    if hasattr(user, 'status') and user.status is not None:
        max_id = user.status.id

    while(True):
        newTweets = api.GetUserTimeline(
            screen_name=screen_name, count=200, max_id=max_id)
        if not newTweets:
            return tweets
        for tweet in newTweets:
            tweet.created_at_date = parseTwitterDate(tweet.created_at)
        earliestTweet = min(newTweets, key=lambda x: x.created_at_date)
        tweets += newTweets
        max_id = earliestTweet.id
        earliestTweetDate = earliestTweet.created_at_date
        print(printDateOnly(earliestTweetDate), end=' ', flush=True)
        if(len(newTweets) == 1 or earliestTweetDate < start):
            return list(filter(lambda x: betweenDates(x.created_at_date, start, end), tweets))


for screen_name in screen_names:
    print("Processing screen name: " + screen_name)
    user = api.GetUser(screen_name=screen_name)

    user.tweets = getTweets(user, startDateString, endDateString)
    print("\r\nGot tweets: " + str(len(user.tweets)))
    user.tweets.sort(key=lambda x: x.created_at_date, reverse=True)
    usersLoaded.append(user)

with open(userOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "followers_count"])
    for user in usersLoaded:
        row = [user.screen_name, user.followers_count]
        csvWriter.writerow(row)

with open(tweetsOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "tweet_id", "created_at", "text"])
    for user in usersLoaded:
        for tweet in user.tweets:
            row = [user.screen_name, tweet.id, printDate(
                tweet.created_at_date), tweet.full_text or tweet.text]
            csvWriter.writerow(row)

print("Done!")
