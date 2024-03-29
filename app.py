from flask import Flask, request, redirect, session, url_for, send_from_directory, Response
from flask_cors import CORS
from flask.json import jsonify
from flask import json
from pprint import pformat
import hashlib
import requests
import urllib
from urllib.parse import urlparse
import logging
import os
import io
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import visualize_data

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}}, headers='Content-Type')

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

# Data filepath
data_path = 'data.json'
image_path = 'temp_img.jpg'
bad_imge_path = 'bad-image.png'

# Constants
success = {'response': 'Success'}
failure = {'response': 'Failure'}

# Debug
@app.route("/debug", methods=["GET"])
def debug():
    myinfo=requests.get(august_rest+'/users/me', headers=headers).json()
    returnjson=requests.get(august_rest+'/users/locks/mine', headers=headers)
    myinfo['locks']=returnjson.json()
    returnjson=requests.get(august_rest+'/doorbells/'+doorbell_id, headers=headers)
    myinfo['doorbell']=returnjson.json()
    return jsonify(myinfo)

# Log
@app.route("/log", methods=["GET"])
def log():
    return send_from_directory('.', 'augustdebug.txt', as_attachment=True, cache_timeout=0)

# Check response.json() matches {'message': 'success'}
def augustSuccess(response):
    return ('message' in response and response['message'] == 'success')

# Display info
@app.route("/")
def info():
    return "OctoberLock backend API"


########
# Stay #
########

# TODO: Fix errors:
#   - check if id in dict
#   - don't start if ended
#   - only one stay at a time

def stayStart(id):
    app.logger.debug('stayStart: enter')

    # TODO: Check if important devices (lock, doorbell, bridge?) online

    data = loadDataFile().json
    if data == failure:
        return jsonify(failure)
    data['Airbnb'][id]['Start_Time'] = nowToStr(dateFormatMinute)
    writeDataFile(data)

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
    return jsonify(success)


def stayEnd(id):
    app.logger.debug('stayEnd: enter')

    data = loadDataFile().json
    if data == failure:
        return jsonify(failure)
    data['Airbnb'][id]['End_Time'] = nowToStr(dateFormatMinute)
    writeDataFile(data)

    # Delete webhook for lock
    response = requests.delete(august_rest+'/webhook/'+lock_id+'/'+client_id, headers=headers).json()
    if not augustSuccess(response):
        return jsonify(response)

    # Delete webhook for doorbell
    return cameraEnd()

def stayAdd(id, guestNum):
    app.logger.debug('stayAdd: enter')

    data = loadDataFile().json
    if data == failure:
        return jsonify(failure)
    data['Airbnb'][id] = {
        'Start_Time': 'Present',
        'End_Time': 'Present',
        'Tot_Guests': guestNum,
        'Entries': []
      }
    writeDataFile(data)
    return jsonify(success)

# Start or end stay, verify devices online
# Pass in {'type':'start', 'id': 'ID', 'guestNum': INT} 
# or {'type': 'end', 'id': 'ID', 'guestNum': INT}
# or {'type': 'add', 'id': 'ID', 'guestNum': INT}
@app.route("/stay", methods=["GET", "POST"])
def stay():
    data = success
    if request.method == "POST":
        req = request.json
    else:
        req = request.args
    if not req:
        app.logger.debug('Error: no POST data')
        return jsonify({'response': 'Error', 'msg': 'no POST data'}), 200
    for key in ['type', 'id', 'guestNum']:
        if key not in req:
            app.logger.debug('Error: undefined key')
            return jsonify({'response': 'Error', 'msg': key+' undefined'}), 200
    if req['type'] == 'start':
        returnjson = stayStart(req['id'])
        if returnjson.json != success:
            app.logger.debug('Error: ' + str(returnjson.json))
            return returnjson
    elif req['type'] == 'end':
        returnjson = stayEnd(req['id'])
        if returnjson.json != success:
            app.logger.debug('Error: ' + str(returnjson.json))
            return returnjson
    elif req['type'] == 'add':
        returnjson = stayAdd(req['id'], req['guestNum'])
        if returnjson.json != success:
            app.logger.debug('Error: ' + str(returnjson.json))
            return returnjson
    else:
        data = {'response': 'Error', 'msg': 'type must be "start" or "end" or "add"'}
    app.logger.debug(str(data))
    return jsonify(data), 200


##################
# Event Handling #
##################

# Debug purposes
responses = []

# Setup webhook for doorbell
def cameraStart():
    body = {
      'url': server_url+'/doorbellResponse',
      'clientID': client_id,
      'header': "augustHeader",
      'token': "doorbellSecret",
      'method': "POST",
      'notificationTypes': ['motiondetected']
    }

    response = requests.post(august_rest+'/webhook/doorbell/'+doorbell_id, headers=headers, json=body).json()
    if not augustSuccess(response):
        return jsonify(response)
    return jsonify(success)

# Delete webhook for doorbell
def cameraEnd():
    response = requests.delete(august_rest+'/webhook/doorbell/'+doorbell_id+'/'+client_id, headers=headers).json()
    if not augustSuccess(response):
        return jsonify(response)
    return jsonify(success)

# Return most recent image for doorbell
def cameraImage():
    # TODO: Download and store image locally
    response = requests.get(august_rest+'/doorbells/32cdfb23111f', headers=headers).json()
    if 'recentImage' in response and 'url' in response['recentImage']:
        return response['recentImage']['url']
    return "error"

# Handle lock events
@app.route("/lockResponse", methods=["POST"])
def lockResponse():
    responses.append(request.json)

    req = request.json
    if req:
        if 'EventType' in req and (req['EventType'] == 'status' or req['EventType'] == 'operation'):
            if 'Event' in req and req['Event'] == 'unlock':
                returnjson = cameraStart()
                if returnjson.json != success:
                    return returnjson
            else:
                returnjson = cameraEnd()
                if returnjson.json != success:
                    return returnjson
    return jsonify(success), 200

#Handle doorbell events
@app.route("/doorbellResponse", methods=["POST"])
def doorbellResponse():
    responses.append(request.json)

    app.logger.debug('doorbellResponse: enter')
    req = request.json
    if req:
        if 'EventType' in req and req['EventType'] == 'doorbell_motion_detected':
            eventTime = datetime.now()
            eventStr = dateToStr(eventTime, dateFormatMinute)
            image = req['Url'] if 'Url' in req else cameraImage()
            numGuests, boxes = process(image)

            app.logger.debug("Doorbell motion: time=%s image=%s num:%s" %
                 (eventStr, image, numGuests))

            data = loadDataFile().json
            if data == failure:
                print("Failed loading json file")
                return jsonify(failure), 200
            print("Loaded json file")
            for id in data['Airbnb']:
                startStr = data['Airbnb'][id]['Start_Time']
                endStr = data['Airbnb'][id]['End_Time']
                if startStr != 'Present':
                    startTime = dateFromStr(startStr, dateFormatMinute)
                    print("Start time", startTime)
                    print("Event time", eventTime)
                    if (startTime <= eventTime) and (endStr == 'Present' or eventTime <= dateFromStr(endStr, dateFormatMinute)):
                        print("To append")
                        data['Airbnb'][id]['Entries'].append({
                            'TimeStamp': eventStr,
                            'NumGuests': numGuests,
                            'Boxes': boxes,
                            'Photo': image,
                          })
            print(data)
            writeDataFile(data)
    return jsonify(success), 200

# Return all responses
@app.route("/responses", methods=["GET"])
def responsesPrint():
    return jsonify(responses)


##################
# Data Retreival #
##################

def initDataFile():
    data =  { "Airbnb": {} }
    writeDataFile(data)

def loadDataFile():
    if not os.path.exists(data_path):
        initDataFile()
    try:
        with open(data_path) as f:
            data = json.load(f)
        f.close()
        return jsonify(data)
    except:
        return jsonify(failure)

def writeDataFile(data):
    with open(data_path, "w+") as f:
        json.dump(data, f)
    f.close()

# Serves data file
@app.route("/data", methods=["GET"])
def data():
    if not os.path.exists(data_path):
        initDataFile()
    return send_from_directory('.', data_path, as_attachment=True, cache_timeout=0)

# Serves plot of entries
@app.route("/plot", methods=["GET"])
def plot():
    try:
        req = request.args
        if not req or 'id' not in req:
            return jsonify(failure)
        fig = visualize_data.stay(req['id'])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return send_from_directory('.', bad_imge_path, as_attachment=True, cache_timeout=0, mimetype='image/png')

# Serves plot of boundings
@app.route("/bounding", methods=["GET"])
def bounding():
    try:
        req = request.args
        if not req or 'id' not in req or 'index' not in req:
            return jsonify(failure)
        fig = visualize_data.bounding(req['id'], req['index'])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return send_from_directory('.', bad_imge_path, as_attachment=True, cache_timeout=0, mimetype='image/png')


####################
# Image Processing #
####################

def saveImage(imgurl):
    urllib.request.urlretrieve(imgurl, image_path)

# Processes jpg from doorbell and return # people entering and array of bounding box dicts
def process(imgurl):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    saveImage(imgurl)

    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    boxes = []
    for object_ in objects:
        if object_.name == "Person":
            boxes.append({
                'obj': object_.name,
                'confidence': object_.score,
                'vertices': [{'x': vertex.x, 'y': vertex.y} for vertex in object_.bounding_poly.normalized_vertices]
                })
    return len(boxes), boxes


##################
# Datetime Utils #
##################

# Predefined date formats
dateFormatDay = "%Y-%m-%d"
dateFormatMinute = "%Y-%m-%d_%H:%M"

# Transforms str to date object
def dateFromStr(dateStr, dateFormat, altFormat=dateFormatDay):
    try:
        return datetime.strptime(dateStr, dateFormat)
    except:
        pass
    try:
        return datetime.strptime(dateStr, altFormat)
    except:
        return datetime.now()

# Transforms UNIX timestamp (milliseconds) to date object
def dateFromInt(timestamp):
    return datetime.fromtimestamp(timestamp // 1000)

# Returns now as a formatted str
def nowToStr(dateFormat):
    return dateToStr(datetime.now(), dateFormat)

# Returns now as a formatted str
def dateToStr(date, dateFormat):
    return date.strftime(dateFormat)


#######
# App #
#######

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
    app.run(host='0.0.0.0', port='8888', debug=True, threaded=True)
