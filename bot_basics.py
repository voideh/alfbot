import os
import json
import time
from slackclient import SlackClient
from api_consumer import get_requests

BOT_NAME = 'alfbot'
BOT_ID = os.environ.get('SLACK_BOT_ID')
AT_BOT = "<@{}>".format(BOT_ID)
SHOW = "show"
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def handle_command(command, channel):
    response = "Sorry, I am a simple robot and can only show you requests. Please start your message with 'show' to continue!"
    if command.startswith(SHOW):
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
        response = "All done!"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    '''
    Basic parsing of all commands directed at the slack bot.
    If an @ is used then he will parse the output to see if he can perform that request
    '''
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel']
    return None, None

if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("ALFBOT READY TO GO")
        api_call = slack_client.api_call("users.list")
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == 'alfbot':
                print("{} {}".format(user.get('name'), user.get('id')))
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Couldn't connect to slack :L")
