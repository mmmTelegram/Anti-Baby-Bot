#!/usr/bin/python
### Import libraries ###
import sys
import time
import telepot
import datetime
import json
import os
from User import User
from threading import Thread
import time
import pytz



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
        modifyTimeUser(userId, choosenTime.tm_hour, choosenTime.tm_min)

    # if the time is not valid, warn the user
    except ValueError:
        messageToUser = "You didn't send me a valid time. Type /time and try it again"
        bot.sendMessage(userId, messageToUser)

### database functions

# delete a user from database by userId
def deleteUser(id):
    del users[id]
    database = open("database.id", "w")
    for user in users:
        insertUser(users[user].userId, users[user].userName, users[user].messageHour, users[user].messageMinute)
    # TALVEZ ESTEJA ERRADO
    #loadUsers()
    return

# modify time info about some user in database by userId
def modifyTimeUser(id, hour, minute):
    users[id].messageHour = hour
    users[id].messageMinute = minute
    database = open("database.id", "w")
    for user in users:
        insertUser(users[user].userId, users[user].userName, users[user].messageHour, users[user].messageMinute)

### Insert user in database.id using json ###
def insertUser(id, name, hour, minute):
    user_struct = {'id' : id, 'name': name, 'hour' :  hour, 'minute' :  minute }
    user_json = json.dumps(user_struct)
    database = open("database.id", "a")
    database.write(user_json + "\n")
    database.close()


### Load users from database.id and add them to users dictionary ###
def loadUsers():
    # creates database.id if it doesnt exists yet
    if not(os.path.isfile("database.id")):
        open("database.id", "w").close()

    with open("database.id", "r") as database:
        for user in database:
            u = json.loads(user)
            newUser = User(u['id'], u['name'], u['hour'], u['minute'])
            users[u['id']] = newUser
            thread = Thread(target = checkTime, args = (u['id'],))
            thread.start()


### Handle messages reiceved from users ###
def chatMessage (message):

    # get the user id
    userId = message['chat']['id']

    # get the user name
    userName = message['chat']['first_name']

    # get the text
    text = message['text']

    # get the time now (on SP)
    timeZone = pytz.timezone('Brazil/East')
    timeNow = datetime.datetime.now(timeZone)
    
    # start the user
    if text == '/start':

        # welcome him and explain how the bot works
        messageToUser = "Hello! I'll help you to remember to take the contraceptive pills."
        messageToUser+= "\nTo change the time to receive alerts, type /time;"
        messageToUser+= "\nTo stop me, type /stop."
        bot.sendMessage(userId, messageToUser)

        # if the user is not already in the dictionary, put it there
        # and then spawn a thread to keep checking if the time to send alert has arrived
        if userId not in users:
            newUser = User(userId, userName, 8, 0)
            users[userId] = newUser
            thread = Thread(target = checkTime, args = (userId,))
            thread.start()

            # check if the user is already in the database
            # if he's not, put it in
            userAlreadyOnDatabase = False
            with open("database.id", "r") as database:
                for user in database:
                    u = json.loads(user)
                    if u['id'] == userId:
                        userAlreadyOnDatabase = True
                if not userAlreadyOnDatabase:
                    insertUser(userId, userName, users[userId].messageHour, users[userId].messageMinute)


    # give some info about the bot
    elif text == '/about':
        messageToUser = "This bot is a free software under GPL v3 and comes without any warranty."
        messageToUser+= "\nCheck the code in https://git.io/vDSYp"
        messageToUser+= "\nFor more infomation, talk to the devs:"
        messageToUser+= "\n@andrealmeid"
        messageToUser+= "\n@leandrohrb"
        bot.sendMessage(userId, messageToUser)

    # the user don't want to receive alerts anymore
    elif userId in users and text == '/stop':
        messageToUser = "If you ever want to receive alerts from me again, type /start"
        messageToUser+= "\nBye bye!"
        bot.sendMessage(userId, messageToUser)
        deleteUser(userId)

    # the user answered if he took the pills or not
    elif userId in users and users[userId].askFlag == 1:
        timeZone = pytz.timezone('Brazil/East')
        timeNow = datetime.datetime.now(timeZone)
        rememberMessage(bot, text, userId, timeNow)

    # the user asked to change the time to receive the alerts
    elif userId in users and text == '/time':
        users[userId].timeFlag = 1

        # convert time to string, to print current time of alert receiving
        printTime = users[userId].hour*3600 + users[userId].minute*60
        printTime = time.gmtime(printTime)
        printTime = time.strftime("%H:%M", printTime)

        # send the message
        messageToUser = "By now, I send you alerts at %s." %printTime
        messageToUser+= "\nTell me the time you want to receive the alerts, in the format HH:MM. For example, '09:30'"
        bot.sendMessage(userId, messageToUser)

    # change the message time (text is the time typed by user, in string format)
    elif userId in users and users[userId].timeFlag == 1:
        changeTime(userId, text)
        users[userId].timeFlag = 0

    # this bot don't like humans, so he won't answer anything else
    elif userId in users:
        messageToUser = "I don't speak humanoide"
        bot.sendMessage(userId, messageToUser)


### Check the time to send the alert message (it's a thread target) ###
def checkTime (userId):

    # keep the thread running
    while True:

        # check if this user still in dictionary, if dont, stop thread
        if userId not in users:
            return

        # send the contraceptive alert, if the time is correct
        timeZone = pytz.timezone('Brazil/East')
        timeNow = datetime.datetime.now(timeZone)
        if timeNow.hour == users[userId].messageHour and timeNow.minute == users[userId].messageMinute:
            alertMessage(userId, bot)
            users[userId].messageHour, users[userId].messageMinute = users[userId].hour, users[userId].minute
            time.sleep(60)

        # if the time is not correct, just wait
        else:
            time.sleep(20)


### Send the alert message for the user ###
def alertMessage (userId, bot):

    # send the message
    messageToUser = "Did you take the pills? Please answer, 'Yes' or 'No'"
    bot.sendMessage(userId, messageToUser)
    users[userId].askFlag = 1


### Send the remember message after 30 minutes, if the user did not took the pills ###
def rememberMessage (bot, text, userId, timeNow):

    # the user took the pills, congratz him
    if text == 'yes' or text == 'Yes':
        messageToUser = "No babies for you, congratulations!!!"
        bot.sendMessage(userId, messageToUser)
        users[userId].askFlag = 0

    # the user did not took the pills, warn him in 30 minutes
    elif text == 'no' or text == 'No':
        messageToUser = "Hmmm... this is bad. I don't like babies. I'll remember you in 30 minutes"
        bot.sendMessage(userId, messageToUser)
        newTime = timeNow + datetime.timedelta(minutes=30)
        users[userId].messageHour, users[userId].messageMinute = newTime.hour, newTime.minute
        users[userId].askFlag = 0

    # if the user answered anything else than 'yes' or 'no', make him answer
    else:
        messageToUser = "Please answer, 'Yes' or 'No'?"
        bot.sendMessage(userId, messageToUser)
        users[userId].askFlag = 1



###############
### Program ###
###############

### get bot token ###
token = getToken ("token.id")

# create bot with it's token
bot = telepot.Bot(token)

# load users from database
loadUsers()

# get inputs from users and handle them
bot.message_loop(chatMessage)

# keep the bot running
while True:
    time.sleep(60)
