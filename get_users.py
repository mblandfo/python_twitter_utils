import twitter
import load_passwords
import csv
import os.path
import sys

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
startDate = "2017-05-01"
endDate = "2017-05-18"

# screen_names = ["cityofindpls", "CityofPhoenixAZ"]
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

for screen_name in screen_names:
    print("Processing screen name: " + screen_name)
    user = api.GetUser(screen_name = screen_name)

    # To create a query_string, go here and fill this out:
    # https://twitter.com/search-advanced
    # %20 is a space
    # %40 is @
    # %23 is #
    # %3A is :
    query_string = "q=from%3A" + user.screen_name + "%20since%3A" + startDate + "%20until%3A" + endDate

    user.tweets = api.GetSearch(raw_query=query_string)    
    usersLoaded.append(user)


with open(userOutputFileName, 'w', newline='') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "followers_count"])
    for user in usersLoaded:
        row = [user.screen_name, user.followers_count]
        csvWriter.writerow(row)

with open(tweetsOutputFileName, 'w', newline='') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(["screen_name", "tweet_id", "created_at", "text"])
    for user in usersLoaded:        
        for tweet in user.tweets:
            row = [user.screen_name, tweet.id, tweet.created_at, tweet.full_text or tweet.text]
            csvWriter.writerow(row)

print("Done!")
