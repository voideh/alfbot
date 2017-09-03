import os
import requests

def get_requests(get=0):
    resp = requests.get("http://localhost:8000/api/requests/?status=A", headers={'Authorization' : 'Token {}'.format(os.environ.get('API_AUTH_TOKEN'))})
    if resp.status_code != 200:
        raise ApiError('GET /api/requests/?status=A {}'.format(resp.status_code))
    if get == 0:
        for request in resp.json():
            yield format_response(request)
    else:
        for x in range(get):
            yield format_response(resp.json()[x])


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


