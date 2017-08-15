import os
import time
import TOKENS
from sys import maxint
from slackclient import SlackClient
from datetime import datetime
from committee import committee

#starterbot's ID variable
BOT_ID = TOKENS.SLACK_BOT_ID

#constants
AT_BOT = "<@" + BOT_ID + ">"

committeeArrayTest = []
#TODO: Setup SQL pulls and sets
pointArray = [100, 90, 90, 85, -1, 0, 0, 0, 0, 0, 40, 40, 30, 30, 10]
committeeArray = ["DISEC", "Security Council", "Joint", "Sec Assistants", "IPC", "Ad Hoc 9/11", "Antebellum Senate",  
    "First National Assembly of Greece", "Global Intel", "Arab League", "UNICEF", "African Union", "UNEP", "SOCHUM", "SpecPol"]
CommitteeCount = 0

#instantiate Slack & Twilic clients
slack_client = SlackClient(TOKENS.SLACK_BOT_TOKEN)

#TODO: Integrate database pulls or a file in/file out (on fail) system
def load_classes_on_startup():
    """
        Assigns names and scores to each committee instance.
    """
    sep = ""

    """
        Prints the loaded committee names
    """
    for x in range(len(committeeArray)):
        committeeArrayTest.append(committee(committeeArray[x], pointArray[x]))

    """
        Sets the global committee count variable
    """
    global CommitteeCount
    CommitteeCount = len(committeeArrayTest)
    
    print "Loaded the following committees:",
    for com in committeeArrayTest:
        print sep+com.name,
        sep = ', '
    print

def get_user_name(userID):
    """
        Gets first name of user stored under passed userID
    """
    if(userID is not TOKENS.SLACK_BOT_ID):
        r = slack_client.api_call("users.info", token = TOKENS.SLACK_API_TOKEN, user = userID)
        """Checks if api call returned a user"""
        if(r['ok']):
            userName = r['user']['profile']['first_name']
            return userName
    return None


def print_all_scores(userID):
    """
        Prints the entire scoreboard, with committees having identical scores on the same line
    """
    scoreBoard = ""
    maxIndex = 0
    committeesAdded = 0
    userName = get_user_name(userID)
    controlArray = [0] * CommitteeCount

    """
        Runs until all committees have been added to the scoreboard
    """
    while committeesAdded < CommitteeCount:
        """
            Reinitializes variables every loop
        """
        committeesAtScore = ""
        max = -maxint - 1
        maxCom = committee()
        maxIndex = -1

        """
            Finds the first committee that hasn't been added to the scoreboard yet
        """
        for index, com in enumerate(committeeArrayTest):
            if(com.score > max and controlArray[index] == 0):
                maxCom = com
                max = com.score
                maxIndex = index
        
        committeesAtScore += maxCom.name
        controlArray[maxIndex] = 1
        committeesAdded += 1

        """
            Finds all committees with identical score of the previous found max and adds their names to the same line
        """
        for index, com in enumerate(committeeArrayTest):
            if(com.score == max and controlArray[index] == 0):
                committeesAtScore += ", " + com.name
                committeesAdded += 1
                controlArray[index] = 1

        """
            Adds line of all committees to the scoreboard
        """
        scoreBoard += committeesAtScore + ": " + str(max) + "\n"

    print userName + " printed the Scoreboard at " + str(datetime.now())
    return scoreBoard

def modify_score(command, operator, userID):
    """
        Modifies score based on operator(+/-) and points passed
        Prints action to console
        Announces to general channel
    """
    var = command.split(" ", 2)
    index = 0
    committeesFound = 0
    foundCommittee = committee()
    response = ""
    userName = get_user_name(userID)
    possibleCommittees = ""

    if(not(userID == TOKENS.JAMES_ID or userID == TOKENS.NOLAN_ID or userID == TOKENS.ZOE_ID or userID == TOKENS.ANJALI_ID)):
        response = userName + " is not authorized to modify scores."
        return response

    """
        Searches the array of committee instances for names containining the 
        passed parameter. Counts instances with names matching the passed
        parameter.
    """
    print "Committee Search begun:"
    for com in committeeArrayTest:
        if(var[2].lower() in com.name.lower()):
            possibleCommittees += com.name + ", "
            foundCommittee = com
            committeesFound += 1
            print "Found match: " + com.name

    if(committeesFound == 0):
        print "Invalid modify command was issued by " + userName + " at " + str(datetime.now())
        response = '*' + var[2] + '* does not match any committee.'
        return response
    
    if(committeesFound > 1):
        """
            Changes last semi-colon to a period. Strings are immutable in python,
            this covoluted mess is the best way to edit strings
        """
        #Removes last comma, appends possible committees to response
        possCommitFormatted = list(possibleCommittees)
        possCommitFormatted[len(possibleCommittees) - 2] = '.'
        possibleCommittees = "".join(possCommitFormatted)
        response = "*" + var[2] + "* was too vague. Possible matches: " + possibleCommittees
        return response

    #Handles invalid integer parameters
    try:
        x = int(var[1])
    except ValueError:
        print "Invalid modify command was issued by " + userName + " at " + str(datetime.now())
        response = "*" + var[1] + "* is not a valid point entry. Try again."
        return response  
    

    
    if(operator == '+'):
        foundCommittee.score += int(var[1])
        response =  userName + " added *" + str(var[1]) + "* points to " + foundCommittee.name + "'s score.\n" + \
            foundCommittee.name + "'s new score is now " + str(foundCommittee.score) + "."
    elif(operator == '-'):
        foundCommittee.score -= int(var[1])
        response = userName + " removed *" + str(var[1]) + "* points from " + foundCommittee.name + "'s score.\n" + \
            foundCommittee.name + "'s new score is now " + str(foundCommittee.score) + "."
    else:
        respone = "*" + operator + "* is not a valid operator. No points added."

    
    print userName + " modified score at " + str(datetime.now())
    return response


def list_commands(userID):
    """
        Returns a list of commands
    """
    commandList = ["scoreboard", "add <score> <committee>", "remove <score> <committee>", "joke", "copypasta", "about"]
    response = "Here's a list of commands:\n"
    userName = get_user_name(userID)


    for x in commandList:
        response += "*" + x + "*\n"

    print userName + " listed commands at " + str(datetime.now())
    return response

def trivia():
    return "Not yet <@" + TOKENS.JENUWINE_ID + "|Michael>"

def about():
    return "Coded in *Python* with :heart: by <@" + TOKENS.JAMES_ID + "|James>"

def copyPasta(command, userID):

    target = command.split(" ", 2)
    
    try:
        pastaName = get_user_name(target[1][2:-1].upper())
    except IndexError:
        pastaName = "None"

    if(pastaName == "None"):
        return "*Invalid command*: Did you @ someone incorrectly?"

    textPasta = "Here is what I have to say about the above paragraph: nobody \"makes a final point\" just for the sake of it. " + \
    "The final point was posted for the purpose of promoting some sort of argument, we can assume within MUNUM itself. " + \
    "In general, we always \"make a final point\" with the purpose of promoting an argument, this is not a controversial fact. " + \
    "So we have to naturally ask ourselves: (a) what argument was " + pastaName + " trying to promote, " + \
    "and (b) what would the effects of this argument being accepted have been on " + pastaName +" himself, his peers, and in general on MUNUM. " + \
    "\nI believe this methodology very quickly lays bare what the \"final point\" truly was, once the obtuse language and logical jumps (whether valid or not) are stripped out. " + \
    "When asking myself these questions, I find it very difficult to come to any conclusion but the following: " + \
    pastaName + "'s ultimate goal was to transform the culture and ideology of MUNUM and perhaps the university as a whole to be more homogeneous and more like him, at the expense of other ideologies."
    
    return textPasta



def handle_command(command, channel, userID):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    outputChannel = channel
    if command.startswith("scoreboard"):
        response = print_all_scores(userID)
    elif command.startswith("joke"):
        #TODO: abstract into another function
        response = "Nicco's virtue signaling about emojis."
    elif command.startswith("copypasta"):
    	response = copyPasta(command, userID)
    elif command.startswith("add"):
        response = modify_score(command, '+', userID)
    elif command.startswith("remove"):
        response = modify_score(command, '-', userID)
    elif command.startswith("list"):
        response = list_commands(userID)
    elif command.startswith("trivia"):
            response = trivia()
    elif command.startswith("about"):
        response = about()
    else:
        print "Recieved an invalid command at " + str(datetime.now())
        response = "Invalid Command. Try *list* for a list of valid commands."

    slack_client.api_call("chat.postMessage", channel=outputChannel,
                                 text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output_list[0]['user']
    return None, None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    
    if len(pointArray) == len(committeeArray):
        if slack_client.rtm_connect():
            load_classes_on_startup()
            print("Scorebot connected and running!")
            while True:
                command, channel, userID = parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    handle_command(command, channel, userID)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
    else:
        print "Committee count " + str(len(committeeArray)) +  " does not match point count " + str(len(pointArray))
