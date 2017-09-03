import os
import time
from slackclient import SlackClient

BOT_NAME = 'alfbot'
BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@{}>".format(BOT_ID)
SHOW = "show"
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def handle_command(command, channel):
    response = "Sorry, I am a simple robot and can only show you requests. Please start your message with 'show' to continue!"
    if command.startswith(SHOW):
        response = "Okay...\nGrabbing some requests now"
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
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Couldn't connect to slack :L")
