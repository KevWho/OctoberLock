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
api_secret = "secret"
debug_explain = ['0: August Credentials',
                 '1: User Auth',
                 '2: Receive Code',
                 '3: Exchange Code for Access Token']
debug_step = int(os.getenv('DEBUG_STEP',len(debug_explain))) # By default, run all steps in debug_explain.

if os.getenv('STAGING', False):
    auth_base='https://staging-oauth.august.com'
    august_rest='https://staging.august.com'
else:
    auth_base='https://auth.august.com'
    august_rest='https://api-production.august.com'

# Constants for August production APIs
authorization_base_url = auth_base+'/authorization'
token_url              = auth_base+'/access_token'

# AUTHCALL must match one of the callbacks you registered with August
# This must be a full url, e.g. https://some.domain.name/some/path
auth_callback = "https://partners.august.com/oauthtest/cb"

# To specify the route in Flask, we just need part of the full auth_callback (no scheme or netloc)
auth_route = urlparse(auth_callback).path


# Step 0: Get the credentials from August
def dumpCredentials():
    hm = hashlib.md5()
    hm.update(api_secret)
    return "<html><body><h2>%s</h2><ul><li>client_id=%s</li><li>partner_secret(md5)=%s</li></ul></body>" % (debug_explain[debug_step], client_id, hm.hexdigest())

# Step 1: Direct the user to the August Auth page
@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. August)
    using an URL with a few key OAuth parameters.
    """
    if debug_step == 0:
        return dumpCredentials()
    
    state=20180209
    parameters=urllib.parse.urlencode({'client_id': client_id,
                                 'redirect_uri': auth_callback,
                                 'state': state})
    authorization_url=authorization_base_url+"?"+parameters

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    if debug_step == 1:
        return "%s\n%s" %(debug_explain[debug_step],authorization_url)
    else:
        return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@app.route(auth_route, methods=["GET"])
def callback():
    """ Step 2: Receive the authorization code.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    app.logger.debug('callback: entered')

    # Use the Flask request object to get the parameters we expect
    # code: the authorization code August generated which you will use in the next step
    # state: the partner_state as above
    code = request.args.get('code')
    app.logger.debug('callback: got code: '+str(code))

    if debug_step == 2:
        return code

    # Step 3: Make the auth call to August to get the access token
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    parameters={'code':code, 'client_secret': api_secret,
                'client_id': client_id, 'grant_type': 'authorization_code'}

    if debug_step == 3:
        return "%s\n%s?%s" % (debug_explain[debug_step], token_url, parameters)
    else:
        authpost=requests.post(token_url, json=parameters)
        app.logger.debug('callback: made authpost')
        app.logger.debug('response data: ' + pformat(authpost))
        token=authpost.json()['access_token']
        app.logger.debug('callback: access_token='+token)
    
        # At this point you can fetch protected resources but lets save
        # the token and show how this is done from a persisted token
        # in /profile.
        session['oauth_token'] = token

        app.logger.debug('callback: redirecting')
    
        return redirect(url_for('.profile'))


# By default this gets a list of all your locks, but if you pass in ?LockID=...
# then you can get the details of a specific lock
@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('profile: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    specificlock = request.args.get('LockID',False)

    myinfo=requests.get(august_rest+'/users/me', headers=headers).json()

    if specificlock:
        returnjson=requests.get(august_rest+'/locks/%s' % specificlock, headers=headers)
    else:
        returnjson=requests.get(august_rest+'/users/locks/mine', headers=headers)

    myinfo['locks']=returnjson.json()
        
    return jsonify(myinfo)

@app.route("/house", methods=["GET"])
def house():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('house: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    returnjson=requests.get(august_rest+'/houses/d7bfbd74-9314-4220-a952-b585035d5869', headers=headers)
        
    return jsonify(returnjson.json())

@app.route("/doorbell", methods=["GET"])
def doorbell():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('doorbell: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    returnjson=requests.get(august_rest+'/doorbells/32cdfb23111f', headers=headers)
        
    return jsonify(returnjson.json())

@app.route("/webRTCBegin", methods=["GET"])
def webRTCBegin():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('webRTCBegin: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    body = {
      'offer': "[sdp offer goes here]",
      'clientTransactionID': 'webRTCTestCall'
    }
    returnjson=requests.post(august_rest+'/doorbells/32cdfb23111f', headers=headers, json=body)
        
    return jsonify(returnjson.json())

@app.route("/webhookLock", methods=["GET"])
def webhookLock():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('webhookLock: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application/json'}

    body = {
      'url': "https://olock.kevin-hu.org/webhookResponse",
      'clientID': client_id,
      'header': "augustHeader",
      'token': "headerSecret",
      'method': "POST",
      'notificationTypes': ['operation']
    }

    returnjson=requests.post(august_rest+'/webhook/11CE24327D5649E0BCC8E79AE3D15D1E', headers=headers, json=body)
        
    return jsonify(returnjson.json())

@app.route("/webhook", methods=["GET"])
def webhook():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('webhook: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application/json'}

    body = {
      'url': "https://olock.kevin-hu.org/webhookResponse",
      'clientID': client_id,
      'header': "augustHeader",
      'token': "headerSecret",
      'method': "POST",
      'notificationTypes': ['videoavailable']
    }

    returnjson=requests.post(august_rest+'/webhook/doorbell/32cdfb23111f', headers=headers, json=body)
        
    return jsonify(returnjson.json())

@app.route("/webhookDelete", methods=["GET"])
def webhookDelete():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('webhookDelete: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    returnjson=requests.delete(august_rest+'/webhook/doorbell/32cdfb23111f/'+client_id, headers=headers)
        
    return jsonify(returnjson.json())

@app.route("/webhookDeleteLock", methods=["GET"])
def webhookDeleteLock():
    """Fetching a protected resource using an OAuth 2 token.
    """

    app.logger.debug('webhookDeleteLock: enter')

    headers={'x-august-api-key': api_key,
             'x-august-access-token': token,
             'content-type': 'application-json'}

    returnjson=requests.delete(august_rest+'/webhook/11CE24327D5649E0BCC8E79AE3D15D1E/'+client_id, headers=headers)
        
    return jsonify(returnjson.json())

webhookResponses = []
@app.route("/webhookResponse", methods=["GET", "POST"])
def webhookResponse():
    if request.method == "GET":
        app.logger.debug('webhookResponse-GET: enter')
        return jsonify({ 'responses': webhookResponses})

    if request.method == "POST":
        webhookResponses.append(request.json)
        data = {'response': 'Success'}
        return jsonify(data), 200

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # This is a Flask thing, used to protect cookies in the session.
    app.secret_key = os.urandom(24)

    # You can get to this with "docker exec <container name> cat augustdebug.txt"
    logging.basicConfig(filename='augustdebug.txt', level=logging.DEBUG)

    app.logger.debug("Startup variables: client_id=%s api_key=%s api_secret=%s auth_callback=%s auth_route=%s debug_step=%d" %
                     (client_id, api_key, api_secret, auth_callback, auth_route, debug_step))
    if debug_step<len(debug_explain):
        app.logger.debug(debug_explain[debug_step])

    # Bind to all interfaces on the host using default port of 5000
    #app.run(host='0.0.0.0')
    # This mode enables a debugger and will auto-reload any new code changes.
    # Using the debugger requires entering a PIN found in "augustdebug.txt".
    app.run(host='0.0.0.0', port='8888', debug=True)
