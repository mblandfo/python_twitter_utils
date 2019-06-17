import twitter
import load_passwords
import load_settings
import csv
import os.path
import sys
import pytz
from datetime import datetime, timedelta
from util import *
import time
from pyquery import PyQuery as pq

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

inputFileName = "big921.csv"
prefix = inputFileName.replace(".csv", " ")
userOutputFileName = prefix + "userOutput.csv"
followingOutputFileName = prefix + "following.csv"
tweetsOutputFileName = prefix + "tweetsOutput.csv"
startDateString = settings["startDateString"]
endDateString = settings["endDateString"]
# Note: for a list of timezones, look at pytz.common_timezones
timezone = pytz.timezone(settings["timezone"])


class CsvLine(object):
    twitterId = None
    screen_name = None
    name = None
    cityId = 0
    cityName = ""
    state = 0
    webAddress = ""
    finalWebAddress = ""
    twitterHandle = ""
    alternateTwitterHandle = ""
    notes = ""
    creationDate = None
    lastTweetDate = None
    twitterAccountDescription = ""
    numberOfLikes = 0
    numberOfFollowers = 0
    numberFollowing = 0
    numberOfTweets = 0
    numberOfLists = 0
    numberOfMedia = 0
    verified = False
    # numberOfPinnedTweets = 0
    email = ""

    followers = []
    following = []
    pinnedTweets = []

    def __init__(self, csvLine):
        # self.twitterHandle = csvLine[0]
        self.cityId = csvLine[0]
        self.cityName = csvLine[1]
        self.state = csvLine[2]
        self.webAddress = csvLine[3]
        self.twitterHandle = csvLine[4]
        # self.alternateTwitterHandle = csvLine[5]
        # self.notes = csvLine[6]

    @staticmethod
    def csv_titles():
        return ["CityName", "State", "WebAddress", "FinalWebAddress", "TwitterHandle", "AlternateTwitterHandle",
                "Notes", "CreationDate", "LastTweetDate", "TwitterAccountDescription",
                "Number of Likes", "Number of Followers", "Number Following", "Email",
                "Name", "Verified", "Number of Tweets", "Number of Lists", "Number of Media"]

    def toCsv(self):
        return [self.cityName, self.state, self.webAddress, self.finalWebAddress, self.twitterHandle, self.alternateTwitterHandle,
                self.notes, printDate(self.creationDate), printDate(
                    self.lastTweetDate), self.twitterAccountDescription, self.numberOfLikes, self.numberOfFollowers, self.numberFollowing,
                self.email, self.name, self.verified, self.numberOfTweets, self.numberOfLists, self.numberOfMedia]


csvLines = []

if not os.path.isfile(inputFileName):
    print("Input file not found: " + inputFileName)
    sys.exit()

with open(inputFileName, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    iterator = iter(csvreader)
    next(iterator)
    for row in iterator:
        csvLine = CsvLine(row)
        csvLines.append(csvLine)
    print("Loaded " + str(len(csvLines)) + " lines from " + inputFileName)

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
            screen_name=screen_name, count=100, max_id=max_id)
        if not newTweets:
            return tweets
        for tweet in newTweets:
            tweet.created_at_date = parseTwitterDate(tweet.created_at)
        earliestTweet = min(newTweets, key=lambda x: x.created_at_date)
        tweets += newTweets
        max_id = earliestTweet.id
        earliestTweetDate = earliestTweet.created_at_date
        print(printDateOnly(earliestTweetDate), end=' ', flush=True)
        if(earliestTweetDate < start and len(tweets) >= 5):
            filtered = list(filter(lambda x: betweenDates(
                x.created_at_date, start, end), tweets))
            if(len(filtered) < 5):
                return getLastNTweets(tweets, 5)
            return tweets
        if(len(newTweets) == 1):
            return tweets


def getLastNTweets(tweets, n):
    tweets.sort(key=lambda x: x.created_at_date, reverse=True)
    return tweets[:5]


with open(tweetsOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "tweet_id", "created_at", "text"])
    for csvLine in csvLines:
        screen_name = csvLine.twitterHandle
        # if(not screen_name or screen_name.strip() == "NA"):
        # screen_name = csvLine.alternateTwitterHandle
        if(screen_name and screen_name.strip() != "NA"):
            idx = -1
            if "@" in screen_name:
                idx = screen_name.index("@")
            if idx > 0:
                screen_name = screen_name[idx:]
            print("Processing screen name: " + screen_name)
            try:
                user = api.GetUser(screen_name=screen_name)
                csvLine.twitterId = user.id
                csvLine.screen_name = screen_name
                csvLine.numberOfTweets = user.statuses_count
                csvLine.name = user.name
                csvLine.creationDate = parseTwitterDate(user.created_at)
                csvLine.numberOfFollowers = user.followers_count
                csvLine.numberFollowing = user.friends_count
                csvLine.twitterAccountDescription = (
                    user.description or "").replace('\n', ' ').replace('\r', '')
                csvLine.email = user.email
                csvLine.numberOfLikes = user.favourites_count
                csvLine.verified = user.verified
                # csvLine.webAddress = user.url
                # csvLine.finalWebAddress = getFinalUrl(user.url)

                # lastTweet = api.GetUserTimeline(screen_name=screen_name, count=1)
                # if lastTweet and lastTweet[0]:
                #     csvLine.lastTweetDate = parseTwitterDate(
                #         lastTweet[0].created_at)
                # print("set user data, sleeping 10")
                # time.sleep(10)
                # doc = pq("https://twitter.com/" +
                #          screen_name.replace('@', '') + "?lang=en")
                # container = doc(
                #     '.ProfileNav-stat--link').filter(lambda i: 'List' in pq(this).text())
                # csvLine.numberOfLists = int((container.find(
                #     '.ProfileNav-value').text() or "0").replace(',', ''))
                # csvLine.numberOfMedia = int(
                #     (doc('.PhotoRail .PhotoRail-headingWithCount').text() or "0").replace(',', '').replace('Photos and videos', '').strip())
                # print("got pyquery data, sleeping 10")
                # time.sleep(10)

                user.tweets = getTweets(user, startDateString, endDateString)
                print("\r\nGot tweets: " + str(len(user.tweets)))
                user.tweets.sort(key=lambda x: x.created_at_date, reverse=True)
                usersLoaded.append(user)
                for tweet in user.tweets:
                    row = [user.screen_name, tweet.id, printDate(
                        tweet.created_at_date), tweet.full_text or tweet.text]
                    csvWriter.writerow(row)
            except Exception as err:
                print("ERROR: " + str(err))


# with open(userOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
#     csvWriter = csv.writer(csvfile)
#     csvWriter.writerow(CsvLine.csv_titles())
#     for csvLine in csvLines:
#         row = csvLine.toCsv()
#         csvWriter.writerow(row)

# with open(followingOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
#     csvWriter = csv.writer(csvfile)
#     csvWriter.writerow(["user", "following screen name", "following name"])
#     for csvLine in csvLines:
#         if csvLine.twitterId:
#             try:
#                 print("Loading friends for: " + csvLine.screen_name)
#                 csvLine.following = list(
#                     map(lambda x: [x.screen_name, x.name], api.GetFriends(user_id=csvLine.twitterId)))
#                 for follow in csvLine.following:
#                     row = [csvLine.screen_name, follow[0], follow[1]]
#                     csvWriter.writerow(row)
#                 csvfile.flush()
#                 print("Wait 30 seconds")
#             except Exception as err:
#                 print("ERROR: " + str(err))
#             time.sleep(20)

with open(tweetsOutputFileName, 'w', newline='', encoding='utf-8') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "tweet_id", "created_at", "text"])
    for user in usersLoaded:
        for tweet in user.tweets:
            row = [user.screen_name, tweet.id, printDate(
                tweet.created_at_date), tweet.full_text or tweet.text]
            csvWriter.writerow(row)

print("Done!")
