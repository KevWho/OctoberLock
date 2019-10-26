from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from flask import json
from pprint import pformat
import hashlib
import requests
import urllib
from urllib.parse import urlparse
import logging
import os

app = Flask(__name__)

# This information is obtained upon registration of a new OAuth
# application with August
client_id = "e06433f4-4bd2-40f6-8e73-d00ff7748420"
api_key = "b88ca079-20c7-407d-97f8-d065eeb87907"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpbnN0YWxsSWQiOiIiLCJhcHBsaWNhdGlvbklkIjoiIiwidXNlcklkIjoiOTIyMzkwMmQtMGE3Ny00OWFkLThlYjAtMmNlODE5OTJjZjdhIiwidkluc3RhbGxJZCI6ZmFsc2UsInZQYXNzd29yZCI6dHJ1ZSwidkVtYWlsIjp0cnVlLCJ2UGhvbmUiOnRydWUsImhhc0luc3RhbGxJZCI6ZmFsc2UsImhhc1Bhc3N3b3JkIjpmYWxzZSwiaGFzRW1haWwiOmZhbHNlLCJoYXNQaG9uZSI6ZmFsc2UsImlzTG9ja2VkT3V0IjpmYWxzZSwiY2FwdGNoYSI6IiIsImVtYWlsIjpbXSwicGhvbmUiOltdLCJleHBpcmVzQXQiOiIyMDIwLTAyLTIzVDA0OjE4OjI5LjUyOVoiLCJ0ZW1wb3JhcnlBY2NvdW50Q3JlYXRpb25QYXNzd29yZExpbmsiOiIiLCJpYXQiOjE1NzIwNjM1MDksImV4cCI6bnVsbCwib2F1dGgiOnsiYXBwX25hbWUiOiJUZXN0IiwiY2xpZW50X2lkIjoiMzZmZjQzNTAtYTIxNy00NmE2LTk1MTMtMDQxNWRjMDlhNmM3IiwiYXBpS2V5IjoiYjg4Y2EwNzktMjBjNy00MDdkLTk3ZjgtZDA2NWVlYjg3OTA3IiwicmVkaXJlY3RfdXJpIjoiaHR0cHM6Ly9wYXJ0bmVycy5hdWd1c3QuY29tL29hdXRodGVzdC9jYiJ9fQ.dbqZkiCdYoFjz6xmCpnkpGm9OB-R8X0DRNw9bD1VhxY"

if os.getenv('STAGING', False):
    auth_base='https://staging-oauth.august.com'
    august_rest='https://staging.august.com'
else:
    auth_base='https://auth.august.com'
    august_rest='https://api-production.august.com'

# Constants for August production APIs
authorization_base_url = auth_base+'/authorization'
token_url              = auth_base+'/access_token'

# Device IDs
house_id = 'd7bfbd74-9314-4220-a952-b585035d5869'
lock_id = '11CE24327D5649E0BCC8E79AE3D15D1E'
doorbell_id = '32cdfb23111f'

# General header to use
headers = {'x-august-api-key': api_key,
           'x-august-access-token': token,
           'content-type': 'application/json'}

# Server url
server_url = 'https://olock.kevin-hu.org'

# Constants
success = {'response': 'Success'}
failure = {'response': 'Failure'}

# Check response.json() matches {'message': 'success'}
def augustSuccess(response):
    return ('message' in response and response['message'] == 'success')

# Display info
@app.route("/")
def info():
    return "OctoberLock backend API"


def stayStart():
    app.logger.debug('stayStart: enter')

    # TODO: Check if important devices online
    # Setup webhook for lock
    body = {
      'url': server_url+'/lockResponse',
      'clientID': client_id,
      'header': "augustHeader",
      'token': "lockSecret",
      'method': "POST",
      'notificationTypes': ['operation']
    }

    response = requests.post(august_rest+'/webhook/'+lock_id, headers=headers, json=body).json()
    if not augustSuccess(response):
        return jsonify(response)

    # Setup webhook for doorbell
    body = {
      'url': server_url+'/webhookResponse',
      'clientID': client_id,
      'header': "augustHeader",
      'token': "doorbellSecret",
      'method': "POST",
      'notificationTypes': ['videoavailable']
    }

    response = requests.post(august_rest+'/webhook/doorbell/'+doorbell_id, headers=headers, json=body).json()
    if not augustSuccess(response):
        return jsonify(response)

    return jsonify(success)


def stayEnd():
    app.logger.debug('stayEnd: enter')
    # Delete webhook for doorbell
    response = requests.delete(august_rest+'/webhook/doorbell/'+doorbell_id+'/'+client_id, headers=headers).json()
    if not augustSuccess(response):
        return jsonify(response)

    # Delete webhook for lock
    response = requests.delete(august_rest+'/webhook/'+lock_id+'/'+client_id, headers=headers).json()
    if not augustSuccess(response):
        return jsonify(response)
        
    return jsonify(success)

# Start or end stay, verify devices online
# Pass in {'type' = 'start'} or {'type' = 'end'}
@app.route("/stay", methods=["POST"])
def stay():
    data = success
    req = request.json
    if req and 'type' in req:
        if req['type'] == 'start':
            returnjson = stayStart()
            if returnjson.json != success:
                return returnjson
        elif req['type'] == 'end':
            returnjson = stayEnd()
            if returnjson.json != success:
                return returnjson
        else:
            data = {'response': 'Error', 'msg': 'type must be "start" or "end"'}
    else:
        data = {'response': 'Error', 'msg': 'type undefined'}
    return jsonify(data), 200


# Handle events
webhookResponses = []
@app.route("/lockResponse", methods=["POST"])
def lockResponse():
    webhookResponses = []
    return jsonify(success), 200


if __name__ == "__main__":
    # This is a Flask thing, used to protect cookies in the session.
    app.secret_key = os.urandom(24)

    # You can get to this with "docker exec <container name> cat augustdebug.txt"
    logging.basicConfig(filename='augustdebug.txt', level=logging.DEBUG)

    app.logger.debug("Startup variables: client_id=%s api_key=%s" %
                     (client_id, api_key))

    # Bind to all interfaces on the host using default port of 5000
    #app.run(host='0.0.0.0')
    # This mode enables a debugger and will auto-reload any new code changes.
    # Using the debugger requires entering a PIN found in "augustdebug.txt".
    app.run(host='0.0.0.0', port='8888', debug=True)
