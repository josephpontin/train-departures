import requests
import os
import json
from flask import render_template,request
import re
import sys

from app import app


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dep')
@app.route('/dep/<station>')
def posts(station=None):

    if re.search("^[A-Za-z]{3}$", station):
        r = requests.get(f'http://api.rtt.io/api/v1/json/search/{station}', auth=(os.environ.get('rtt_uname'), os.environ.get('rtt_pword')))
        print(r.json(), file=sys.stderr)
        if 'error' in r.json():
            not_3ALPHA = True
            return search()
        else:
            result = r.json()

            name = str(result['location']['name'])
            
            services = result['services']

            trains = []

            if not services:
                return render_template('depboard.html', station=name, trains=None)

            for service in services:
                train = {}
                try:
                    booked_dep = service["locationDetail"]["gbttBookedDeparture"]
                except:
                    booked_dep = '????'

                train['booked_dep'] = booked_dep

                try:
                    destinations = [destination["description"] for destination in service["locationDetail"]["destination"]]
                    dest_str = ' & '.join(destinations)
                except:
                    dest_str = '??????????'

                train['dest_str'] = dest_str

                try:
                    exp_dep = service["locationDetail"]["realtimeDeparture"]
                    if exp_dep==booked_dep:
                        exp_dep = 'On Time'
                except:
                    exp_dep = '----'

                train['exp_dep'] = exp_dep

                if service['serviceType'] != 'train':
                    platform = service['serviceType'].upper()
                else:
                    try:
                        platform = service["locationDetail"]["platform"]
                    except:
                        platform = '-'

                train['platform'] = platform
                train['operator'] = service['atocName']

                trains.append(train)

            return render_template('depboard.html', station=name, trains=trains)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search', methods = ['POST'])
def search_post():
    code = request.form['Station']

    return posts(station=code)