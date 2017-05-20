import os.path
import runpy
import sys

example = """#--------------------------------------------------------------------------------
# These tokens are needed for user authentication.
# Credentials can be generates via Twitter's Application Management:
#	https://apps.twitter.com/app/new
#--------------------------------------------------------------------------------

consumer_key = "XxXxXxxXXXxxxxXXXxXX"
consumer_secret = "XxXxXxxXXXxxxxXXXxXX"
access_token_key = "XxXxXxxXXXxxxxXXXxXX-XxXxXxxXXXxxxxXXXxXX"
access_token_secret = "XxXxXxxXXXxxxxXXXxXX"
"""

passwordPath = "./passwords.py"

def load():
    if os.path.isfile(passwordPath):
        config = runpy.run_path(passwordPath)
        if config["consumer_key"] == "XxXxXxxXXXxxxxXXXxXX":
            print("You will need to create a twitter app and fill in the values in passwords.py. Exiting...")
            sys.exit()
        return config
    
    with open(passwordPath, 'w') as passwords:
        passwords.write(example)
    
    print("Created passwords.py. You will need to create a twitter app and fill in the values in passwords.py. Exiting...")
    sys.exit()
