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



### Change user time to receive alerts ###
def changeTime (userId, choosenTime):

    # check if time is valid and then change the alert time
    try:

        # transform string to time object
        choosenTime = time.strptime(choosenTime, "%H:%M")

        # change everyday time to receive alert
        users[userId].hour = choosenTime.tm_hour
        users[userId].minute = choosenTime.tm_min

        # change today time to receive alert
        users[userId].messageHour = users[userId].hour
        users[userId].messageMinute = users[userId].minute

        # convert time to string, to print current time of alert receiving
        printTime = users[userId].hour*3600 + users[userId].minute*60
        printTime = time.gmtime(printTime)
        printTime = time.strftime("%H:%M", printTime)

        # warn the user that he changed the time
        messageToUser = "Alright, now the upcoming alerts I'll send you will be at %s" %printTime
        bot.sendMessage(userId, messageToUser)

    # if the time is not valid, warn the user
    except ValueError:
        messageToUser = "You didn't send me a valid time. Type /time and try it again"
        bot.sendMessage(userId, messageToUser)



### Handle messages reiceved from users ###
def chatMessage (message):

    # get the user name
    userName = message['chat']['first_name']

    # get the user id
    userId = message['chat']['id']

    # get the text
    text = message['text']

    # get the time now
    timeNow = datetime.datetime.now()

    # if nobody sent a message, leave
    if userId == 0:
        return

    # create an user object
    newUser = User(userId, userName)

    # if the user is not already in the dictionary, put it there
    # and then spawn a thread to keep checking if the time to send alert has arrived
    if userId not in users:
        users[userId] = newUser
        thread = Thread(target = checkTime, args = (userId,))
        thread.start()

    # welcome the user
    if text == '/start':
        messageToUser = "Hello! I'll help you to remember to take the contraceptive pills.\nTo change the time to receive alerts, type /time"
        bot.sendMessage(userId, messageToUser)

    # the user answered if he took the pills or not
    elif users[userId].askFlag == 1:
        timeNow = datetime.datetime.now()
        rememberMessage(bot, text, userId, timeNow)

    # the user asked to change the time to receive the alerts
    elif text == '/time':
        users[userId].timeFlag = 1

        # convert time to string, to print current time of alert receiving
        printTime = users[userId].hour*3600 + users[userId].minute*60
        printTime = time.gmtime(printTime)
        printTime = time.strftime("%H:%M", printTime)

        # send the message
        messageToUser = "By now, I send you alerts at %s.\nTell me the time you want to receive the alerts, in the format HH:MM. For example, '09:30'" %printTime
        bot.sendMessage(userId, messageToUser)

    # change the message time (text is the time typed by user, in string format)
    elif users[userId].timeFlag == 1:
        changeTime(userId, text)
        users[userId].timeFlag = 0

    # this bot don't like humans, so he won't answer anything else
    else:
        messageToUser = "I don't speak humanoide"
        bot.sendMessage(userId, messageToUser)



### Check the time to send the alert message (it's a thread target) ###
def checkTime (userId):

    # keep the thread running
    while True:

        # send the contraceptive alert, if the time is correct
        timeNow = datetime.datetime.now()
        if timeNow.hour == users[userId].messageHour and timeNow.minute == users[userId].messageMinute:
            alertMessage(userId, bot)
            users[userId].messageHour, users[userId].message_minute = users[userId].hour, users[userId].minute
            time.sleep(60)

        # if the time is not correct, just wait
        else:
            time.sleep(20)



### Send the alert message for the user ###
def alertMessage (userId, bot):

    # send the message
    messageToUser = "Did you took the pills? Please answer 'yes' or 'no'"
    bot.sendMessage(userId, messageToUser)
    users[userId].askFlag = 1



### Send the remember message after 30 minutes, if the user did not took the pills ###
def rememberMessage (bot, text, userId, timeNow):

    # the user took the pills, congratz him
    if text == 'yes':
        messageToUser = "No babies for you, congratulations! See you tomorrow."
        bot.sendMessage(userId, messageToUser)
        users[userId].askFlag = 0

    # the user did not took the pills, warn him in 30 minutes
    elif text == 'no':
        messageToUser = "Hmmm... this is bad. I don't like babies. I'll remember you in 30 minutes"
        bot.sendMessage(userId, messageToUser)
        newTime = timeNow + datetime.timedelta(minutes=30)
        users[userId].message_hour, users[userId].message_minute = newTime.hour, newTime.minute
        users[userId].askFlag = 0

    # if the user answered anything else than 'yes' or 'no', make him answer
    else:
        messageToUser = "Please answer, 'yes' or 'no'?"
        bot.sendMessage(userId, messageToUser)
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
