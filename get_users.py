import twitter
import load_passwords
import csv
import os.path
import sys
import pytz
from datetime import datetime, timedelta

config = load_passwords.load()

api = twitter.Api(consumer_key=config["consumer_key"],
                consumer_secret=config["consumer_secret"],
                access_token_key=config["access_token_key"],
                access_token_secret=config["access_token_secret"],
                sleep_on_rate_limit=True,
                tweet_mode="extended")

inputFileName = "input.csv"
userOutputFileName = "usersOutput.csv"
tweetsOutputFileName = "tweetsOutput.csv"
startDateString = "2017-05-01"
endDateString = "2017-05-18" #endDate is inclusive
# Note: for a list of timezones, look at pytz.common_timezones
timezone = pytz.timezone("America/Phoenix")

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
    print("Loaded " + str(len(screen_names)) + " twitter screen names from " + inputFileName)

usersLoaded = []

def parseDate(dateString):
    d = datetime.strptime(dateString, apiDateFormat)
    return datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, timezone)

def parseTwitterDate(dateString):
    return datetime.strptime(dateString, twitterDateFormat)

def betweenDates(x, start, end):
    return start <= x and x <= end

def getTweets(screen_name, startDateString, endDateString):
    tweets = []
    start = parseDate(startDateString)
    end = parseDate(endDateString) + timedelta(days=1)
    
    earliestTweet = None

    since_id = None
    while(True):
        newTweets = api.GetUserTimeline(screen_name=screen_name, count=200, since_id=since_id)
        if not newTweets:
            return tweets
        for tweet in newTweets:
            tweet.created_at_date = parseTwitterDate(tweet.created_at)
        earliestTweet = min(newTweets, key=lambda x: x.created_at_date)
        tweets += newTweets
        since_id = earliestTweet.id
        earliestTweetDate = earliestTweet.created_at_date
        if(len(newTweets) < 200 or earliestTweetDate < start):
            return list(filter(lambda x: betweenDates(x.created_at_date, start, end), tweets))

for screen_name in screen_names:
    print("Processing screen name: " + screen_name)
    user = api.GetUser(screen_name = screen_name)


    # Note: api.GetSearch had problems returning any data, I filed a bug report: https://github.com/bear/python-twitter/issues/478

    # To create a query_string, go here and fill this out:
    # https://twitter.com/search-advanced
    # %20 is a space
    # %40 is @
    # %23 is #
    # %3A is :
    #query_string = "q=from%3A" + user.screen_name + "%20since%3A" + startDate + "%20until%3A" + endDate
    #query_string = "q=from%3Acityofmentor%20since%3A2017-01-01%20until%3A2017-05-16"
    #user.tweets = api.GetSearch(raw_query=query_string)    

    user.tweets = getTweets(screen_name, startDateString, endDateString)
    user.tweets.sort(key = lambda x: x.created_at_date, reverse=True)
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
            row = [user.screen_name, tweet.id, tweet.created_at_date.isoformat(), tweet.full_text or tweet.text]
            csvWriter.writerow(row)

print("Done!")
