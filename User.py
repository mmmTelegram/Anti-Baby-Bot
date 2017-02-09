### Import libraries ###
import sys



### User Class ###
class User:
    
    ### Time to receive alerts ###
    hour = 1
    minute = 51


    
    ### Init method (constructor)
    def __init__ (self, userId, userName):
        
        # get user id
        self.userId = userId
        
        # get user name
        self.userName = userName
        
        # select the time to receive alert
        self.messageHour = self.hour
        self.messageMinute = self.minute
        
        # This flag is up when the bot is asking for the user to answer 'yes' or 'no'
        # This flas is down after the user answer it
        self.askFlag = 0



