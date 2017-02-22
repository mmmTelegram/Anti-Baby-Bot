### Import libraries ###
import sys


### User Class ###
class User:

    ### Init method (constructor)
    def __init__ (self, userId, userName, userHour, userMinute):

        # get user id
        self.userId = userId

        # get user name
        self.userName = userName
        
        # time to receive alerts everyday
        self.hour = userHour
        self.minute = userMinute

        # select the time to receive alert today (can change if user forget to take the pills)
        self.messageHour = userHour
        self.messageMinute = userMinute

        # This flag is up when the bot is asking for the user to answer 'yes' or 'no'
        # This flas is down after the user answer it
        self.askFlag = 0

        # This flag is up when the bot is asking for the user to answer 'yes' or 'no'
        # This flas is down after the user answer it
        self.timeFlag = 0
