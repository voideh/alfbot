import os
import json
import time
from slackclient import SlackClient
from api_consumer import get_requests, get_by_user, NoRequests

READ_WEBSOCKET_DELAY = 1
BOT_NAME = 'alfbot'
BOT_ID = os.environ.get('SLACK_BOT_ID')
AT_BOT = "<@{}>".format(BOT_ID)
SHOW = "show"
ASK = "anything for me?"
HELP = "help"
TEST = "test"
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

DAYS = { 'monday' : 1, 
        'tuesday' : 2, 
        'wednesday' : 3, 
        'thursday' : 4, 
        'friday' : 5 }

def get_by_day(command, channel, userorigin):
    response = "Okay, what day are you looking for requests from?"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True, mrkdown=True)
    while True: 
        command, channel, user = parse_slack_output(slack_client.rtm_read())
        print(command, channel, user)
        slack_client.api_call("chat.postMessage", channel=channel, text="Got it getting requests for {}".format(command), as_user=True, mrkdown=True)
        if command and channel and user == userorigin:
            if command.lower() in DAYS.keys():
                response = get_requests(day=DAYS.get(command.lower()))
                for message in response:
                    msg = json.dumps([
                        {
                        "text": message,
                        "color" : "#3AA3e3",
                        "attachment_type" : "default",
                        "mrkdwn_in" : ["text"],
                        }])
                    slack_client.api_call("chat.postMessage", channel=channel, text="Request", attachments = msg, as_user=True, mrkdown=True)
                return "All done!"
        time.sleep(READ_WEBSOCKET_DELAY)

def get_sessions(command, channel):
        commands = command.split(' ')
        if len(commands) > 1:
            num = int(commands[-1])
        else:
            num = 0
        response = "Okay...\nGrabbing some requests now"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = get_requests(get=num)
        for message in response:
            msg = json.dumps([
                {
                "text": message,
                "color" : "#3AA3e3",
                "attachment_type" : "default",
                "mrkdwn_in" : ["text"],
                }])
            slack_client.api_call("chat.postMessage", channel=channel, text="Request", attachments = msg, as_user=True, mrkdown=True)
        return "All done!"

def get_session_by_user(uid, channel):
    user = slack_client.api_call('users.info', user=uid)
    if user['ok'] == True:
        message = "Hello {} i'm looking for your sessions now...".format(user['user']['profile'].get('real_name'))
        print("Found valid user")
        print(user['user']['profile'].get('email'))
        slack_client.api_call("chat.postMessage", text=message, channel = channel)
        try:
            response = get_by_user(user['user']['profile'].get('email'))
            for message in response:
                msg = json.dumps([
                    {
                    "text": message,
                    "color" : "#3AA3e3",
                    "attachment_type" : "default",
                    "mrkdwn_in" : ["text"], }])

                slack_client.api_call("chat.postMessage", channel=channel, text="Request", attachments = msg, as_user=True, mrkdown=True)
            return "All done!"
        except NoRequests:
            return "Sorry there's nothing for you at the moment!"
    else:
        return "I don't know what happened"

def handle_command(command, channel, user):
    response = "Sorry, I am a simple robot and can only show you requests. Try typing 'help' to get my valid commands!"
    if command == 'show by day':
        response = get_by_day(command, channel, user)
    elif command.startswith(SHOW):
        response = get_sessions(command, channel)
    elif command.startswith(HELP):
        response = """\
        Here are some basic commands I can execute!
        *anything for me?*\t Show tutoring requests open for you.
        *show [int x : 0 < x < infinity]*?\t Show x amount of tutoring requests. If no number is provided all open requests will be shown.
        """
    elif command == ASK:
        response = get_session_by_user(user, channel)
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True, mrkdown=True)

def parse_slack_output(slack_rtm_output):
    '''
    Basic parsing of all commands directed at the slack bot.
    If an @ is used then he will parse the output to see if he can perform that request
    '''
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return (output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user'])
    return None, None, None


if __name__ == '__main__':
    if slack_client.rtm_connect():
        print("ALFBOT READY TO GO")
        api_call = slack_client.api_call("users.list")
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == 'alfbot':
                print("{} {}".format(user.get('name'), user.get('id')))
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            print(command, channel, user)
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Couldn't connect to slack :L")
