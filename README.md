# Python Twitter Utils

### Install:

Install git for windows https://git-scm.com/download/win  
Install Miniconda for Python 3.6, 64-bit https://conda.io/miniconda.html  
Install Visual Studio Code  

Open a terminal (command prompt) and run these commands:  
```
cd c:\  
mkdir dev  
cd dev  
git clone https://github.com/mblandfo/python_twitter_utils.git
```

Open Visual Studio Code, open directory c:\dev\python-twitter-utils  
In the file picker on the left of Visual Studio Code, select get_users.py
It should ask you about installing the python extension. Click it and pick the top option for Python by Don Jayamanne
Go to File -> Preferences -> Settings and on the right side add this line:  
```
"python.linting.enabled": false
```  
If you want to change your theme go to File -> Preferences -> Color Theme  
  
Restart Visual Studio Code  
  
Go to View -> Integrated Terminal and run this:  

```
pip install python-twitter
```

In Visual Studio Code, open "get_users.py" and right click and select "Run python file in terminal"  (or you can just type "python get_users.py" in the terminal)
It should give you an error saying you need to put in passwords. Help on that is here:  

Create a Twitter App so you can get auth tokens:
https://python-twitter.readthedocs.io/en/latest/getting_started.html  

After that you'll need to look over the settings at the top of get_users.py, and create an input.csv with the screen_names you'd like to get tweets from.
