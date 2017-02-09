### Import libraries ###
import sys
import time
import telepot
import datetime
from User import User
from threading import Thread



### Create users dictionary ###
users = {}



### Get bot token ###
def getToken (file):
    with open (file, "r") as tokenFile:
        return tokenFile.read().replace('\n', '')

    

### Handle messages reiceved from users ###
def chatMessage (message):

    # get the user name
    userName = message['chat']['first_name']

    # get the user id
    userId = message['chat']['id']

    # if nobody sent a message, leave
    if userId == 0:
        return

    # create an user object
    newUser = User(userId, userName)

    # if the user is not already in the dictionary, put it there
    # and then spawn a thread
    if userId not in users:
        users[userId] = newUser
        thread = Thread(target = checkTime, args = (userId,))
        thread.start()
    
    # get the text
    text = message['text']

    # get the time now
    timeNow = datetime.datetime.now()

    # welcome the user
    if text == '/start':
        text = "Hello! I'll help you to remember to take the contraceptive pills!"
        bot.sendMessage(userId, text)
    
    # the user answered if he took the pills or not
    elif users[userId].askFlag == 1:
        timeNow = datetime.datetime.now()
        rememberMessage(bot, text, userId, timeNow)

    # this bot don't like humans, so he will not answer anything else
    else:
        text = "I don't speak humanoide."
        bot.sendMessage(userId, text)



### Check the time to send the alert message (it's a thread target) ###
def checkTime (userId):

    # keep the thread running
    while True:
        
        # send the contraceptive alert, if the time is correct
        timeNow = datetime.datetime.now()
        if timeNow.hour == users[userId].messageHour and timeNow.minute == users[userId].messageMinute:
            alertMessage(userId, bot)
            users[userId].messageHour, users[userId].message_minute = 17, 6
            time.sleep(60)
        
        # if the time is not correct, just wait
        else:
            time.sleep(20)



### Send the alert message for the user ###
def alertMessage (userId, bot):

    # send the message
    alertMessage = "Did you took the pills? Please answer 'yes' or 'no'"
    bot.sendMessage(userId, alertMessage)
    users[userId].askFlag = 1



### Send the remember message after 30 minutes, if the user did not took the pills ###
def rememberMessage (bot, text, userId, timeNow):

    # the user took the pills, congratz him
    if text == 'yes':
        bot.sendMessage(userId, "No babies for you, congratulations!!!")
        users[userId].askFlag = 0

    # the user did not took the pills, warn him in 30 minutes
    elif text == 'no':
        bot.sendMessage(userId, "Hmmm... this is bad. I don't like babies! I'll remember you in 30 minutes")
        newTime = timeNow + datetime.timedelta(minutes=30)
        users[userId].message_hour, users[userId].message_minute = newTime.hour, newTime.minute
        users[userId].askFlag = 0
        
    # if the user answered anything else than 'yes' or 'no', make him answer
    else:
         bot.sendMessage(userId, "Please answer, 'yes' or 'no'?")
         users[userId].askFlag = 1

         

###############
### Program ###
###############

### get bot token ###
token = getToken ("token")

# create bot with it's token
bot = telepot.Bot(token)

# get inputs from users and handle them
bot.message_loop(chatMessage)

# keep the bot running
while True:
    pass
