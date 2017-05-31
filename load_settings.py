import os.path
import runpy
import sys

example = """
inputFileName = "input.csv"
userOutputFileName = "usersOutput.csv"
tweetsOutputFileName = "tweetsOutput.csv"
startDateString = "2017-05-01"
endDateString = "2017-05-18" #endDate is inclusive

# Note: for a list of timezones, look at pytz.common_timezones
timezone = "America/Phoenix"
"""

settingsPath = "./settings.py"

def load():
    if os.path.isfile(settingsPath):
        return runpy.run_path(settingsPath)
    
    with open(settingsPath, 'w') as settings:
        settings.write(example)
    
    print("Created settings.py. You will want to fill in settings there. Exiting...")
    sys.exit()
