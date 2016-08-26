#!/usr/local/bin/python3

import sys
import re
import StringHandler
import requests
import time
from syscmd import syscall

# globals
proxyDict = {}
    
# end initVoiceAssignments

class MacVoice:
    def __init__(self):
        self.presetNames = ['Agnes',
                            'Alex',
                            'Bruce',
                            'Daniel',
                            'Fiona',
                            'Fred',
                            'Karen',
                            'Moira',
                            'Vicki',
                            'Victoria',
                            'Samantha',
                            ]
        
        self.userMappings = {}
        self.voiceAssignments = {}
        self.assignmentOrder = []
        
        for voice in self.presetNames:
            self.voiceAssignments[voice] = None
            self.assignmentOrder.append(voice)
    # end init
        
    def getVoiceForUser(self, id):
        userVoice = None
        
        if id in self.userMappings: 
            if self.userMappings[id]:
                # if user has an assigned voice, use that
                userVoice = self.userMappings[id] 
            
        else:
            for voice in self.voiceAssignments:
                if self.voiceAssignments[voice] is None:
                    # if there is an unassigned voice, use that
                    userVoice = voice
                    break
            
            # if no unassigned user voice was found
            # then we need to steal the oldest voice
            if not userVoice:
                userVoice = self.assignmentOrder[0]
        
        # reassign voice if user keeps same voice, pushes their voice to the
        # back of the reassignment que
        self.assignVoiceToUser(userVoice, id)
        return userVoice
        
    # end getVoiceForUser
    
    
    def assignVoiceToUser(self, voice, id):
        # remove old user mappings
        if self.voiceAssignments[voice]:
            oldUserId = self.voiceAssignments[voice]
            self.userMappings[oldUserId] = None
        
        # move the voice to the back of the assignment order que
        self.assignmentOrder.remove(voice)
        self.assignmentOrder.append(voice)
        
        # assign the voice to the new user
        self.voiceAssignments[voice] = id
        self.userMappings[id] = voice
        
    # end assignVoiceToUser
    
# end Class MacVoice


def getSlackToken():
    with open('slackToken', 'rt') as fID:
        for line in fID:
            if line:
                token = line
    return token
# end getSlackToken

def getChannelId(channelName):
    # experiences channel hardcoded for now
    channelId = ''
    for c in slackVars['channels']:
        if c['name'] == channelName:
            channelId =  c['id']
    
    if not channelId:
        raise LookupError('no channel named: ' + channelName)
    return channelId
# end getChannelId

def getUsers():
    reqParams = {'token': slackVars['token']
                }
    
    slackUsersResp = requests.get("https://slack.com/api/users.list", 
                                    params=reqParams,
                                    stream=False, 
                                    proxies=proxyDict
                                    )

    
    try:
        if not slackUsersResp.status_code == 200:
            raise ConnectionError('slack response code /= 200')
            
        slackUsersDict = slackUsersResp.json()
        members = slackUsersDict['members']
        users = {}
        for m in members:
            id = m['id']
            users[id] = m
            
    except:
        users= {}
        
    return users
# getUsers

def getChannels():
    reqParams = {'token': slackVars['token']
                }
    
    slackChannelsResp = requests.get("https://slack.com/api/channels.list", 
                                    params=reqParams,
                                    stream=False, 
                                    proxies=proxyDict
                                    )

    
    try:
        if not slackChannelsResp.status_code == 200:
            raise ConnectionError('slack response code /= 200')
            
        slackChannelsDict = slackChannelsResp.json()
        channels = slackChannelsDict['channels']
    except:
        channels= []
        
    return channels
# end getChannels

def getLatestMessages(lastReadTimeStamp=None, count=100):
    
    reqParams = {'token': slackVars['token'],
                 'channel': slackVars['channelId'],
                 'count': count,
                 'oldest': lastReadTimeStamp
                 }
    
    slackHistoryResp = requests.get("https://slack.com/api/channels.history", 
                                    params=reqParams,
                                    stream=False, 
                                    proxies=proxyDict
                                    )
    
    
    try:
        if not slackHistoryResp.status_code == 200:
            raise ConnectionError('slack response code /= 200')
            
        slackHistoryDict = slackHistoryResp.json()
        latestMessages = slackHistoryDict['messages']
    except:
        latestMessages = []
        
    return latestMessages
# end getLatestMessages

def speak(text, userId):
    voice = macVoice.getVoiceForUser(userId)
    text = sanitiseTextToSpeach(text)
    print(msg['text'])
    syscall('say -v ' + voice + ' ' + text)
# end speak

def sanitiseTextToSpeach(text):
    text = re.sub('<https?.*?>', 'URL link', text)
    #text = re.sub('<@.*?>', '', text)
    
    # replace <@U796899> with 'at first_name'
    StripAt = StringHandler.StripRegex('<@.*?>')
    StripAt.Strip(text)
    # change all the striped groups
    for g, atRef in enumerate(StripAt.groups):
        id_mo = re.search('<@(.*?)>', atRef)
        try:
            id = id_mo.group(1)
            if slackVars['members'][id]['profile']['first_name']:
                userFirstName = slackVars['members'][id]['profile']['first_name']
            elif slackVars['members'][id]['real_name']:
                userFirstName = slackVars['members'][id]['real_name']
            elif slackVars['members'][id]['name']:
                userFirstName = slackVars['members'][id]['name']
        except:
            userFirstName = ''
            
        if userFirstName:
            StripAt._StripRegex__groups[g] = 'at ' + userFirstName
        else:
            StripAt._StripRegex__groups[g] = ''
    # include all the striped groups
    StripAt.IncludeGroups = [i for i in range(len(StripAt.groups))]
    text = StripAt.StrippedString
    
    text = re.sub('_', ' ', text)
    text = re.sub('&amp;', ' and ', text)
    text = re.escape(text)
    return text
# end sanitiseTextToSpeach


slackVars = {}
def populateSlackVars(channelName):
    slackVars['token'] = getSlackToken()
    slackVars['channels'] = getChannels()
    slackVars['channelId'] = getChannelId(channelName)
    slackVars['members'] = getUsers()
# end getSlackVars

def setMode(modeName):
    if modeName == 'wallsHaveEars':
        channelName = 'general'
        populateSlackVars(channelName) 
        latestTimeStamp = 1472028811
    elif modeName == 'quickDemo':
        channelName = 'experiences'
        populateSlackVars(channelName)  
        latestMessages = getLatestMessages(count=50)
        latestTimeStamp = latestMessages[-1]['ts']
    elif modeName == 'test':
        channelName = 'bottest'
        populateSlackVars(channelName)  
        latestMessages = getLatestMessages(count=1)
        latestTimeStamp = latestMessages[0]['ts']
    else:  
        channelName = modeName
        populateSlackVars(channelName)
        latestMessages = getLatestMessages(count=1)
        latestTimeStamp = latestMessages[0]['ts']
        
    return latestTimeStamp
            
# end setMode
    

if __name__ in ['__main__']:
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'general'

    latestTimeStamp = setMode(mode)
      
    macVoice = MacVoice()
    
    while True:
        latestMessages = getLatestMessages(latestTimeStamp)
        if latestMessages:
            latestTimeStamp = latestMessages[0]['ts']
        latestMessages.reverse()
        for msg in latestMessages:
            speak(msg['text'], msg['user'])
        time.sleep(5)

    
