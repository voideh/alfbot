import os
import requests

class NoRequests(Exception):
    pass

PROTOCOL = "http"
ROOT =  "localhost:8000"
AUTH_HEADS = {'Authorization' : 'Token {}'.format(os.environ.get('API_AUTH_TOKEN')) }

def get_requests(get=0):
    resp = requests.get("{}://{}/api/requests/?status=A".format(PROTOCOL, ROOT), headers=AUTH_HEADS)
    if resp.status_code != 200:
        raise ApiError('GET /api/requests/?status=A {}'.format(resp.status_code))
    if get == 0:
        for request in resp.json():
            yield format_response(request)
    else:
        for x in range(get):
            yield format_response(resp.json()[x])

def get_by_user(email):
    resp = requests.get("{}://{}/api/requests/?availability__ambassador__email={}".format(PROTOCOL, ROOT, email), headers=AUTH_HEADS)
    if resp.status_code != 200:
        raise ApiError("GET /api/requests/?availability__ambassador__email={} {}".format(email, resp.status_code))
    else:
        if not resp:
            raise NoRequests
        else:
            for request in resp.json():
                yield format_response(request)


def format_response(request):
    return """
    *Student* : {}
    *Ambassador*: {}
    *Day*: {}
    *Time*: {} - {}
    *Course*: {}
    """.format(
    request['submitted_by'],
    request['availability']['ambassador'], 
    request['availability']['day'], 
    request['availability']['start_time'],
    request['availability']['end_time'],
    request['course'],)


