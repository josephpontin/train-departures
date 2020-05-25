import requests
import os
import json
from flask import render_template,request
import re
import sys

from app import app

from app import setup

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dep')
@app.route('/dep/<station>')
def posts(station=None):
    def get_results(station, r=None):

        if not r:
            r = requests.get(f'http://api.rtt.io/api/v1/json/search/{station}', auth=(os.environ.get('rtt_uname'), os.environ.get('rtt_pword')))
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


    # Check if input looks like 3 letter station code
    if re.search("^[A-Za-z]*$", station):
        # If it does, give it a go
        r = requests.get(f'http://api.rtt.io/api/v1/json/search/{station}', auth=(os.environ.get('rtt_uname'), os.environ.get('rtt_pword')))
        
        # If no error return the results
        if 'error' not in r.json():
            return get_results(station, r)

    # Check if input looks like station name
    if re.search("^[A-Za-z\s]*$", station):
        
        # Check if exact match
        possible_matches = []
        for key in setup.location_dict:
            if re.search(f'^({station})$', key, re.IGNORECASE):
                print(setup.location_dict[key], file=sys.stderr)
                return get_results(setup.location_dict[key])
            if re.search(f'.*({station}).*', key, re.IGNORECASE):
                possible_match={}
                possible_match['code'] = setup.location_dict[key]
                possible_match['description'] = key.title()
                possible_matches.append(possible_match)
        if len(possible_matches) == 0:
            return render_template('search.html')
            
        # if len(possible_matches) > 20:
        #     # Placeholder, return error about too many matches
        #     return render_template('error.html')
        else:
            possible_matches = sorted(possible_matches, key=lambda k: k['description'])
            return render_template('matches.html', matches = possible_matches)
        return render_template('search.html')

    return render_template('search.html')

    

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search', methods = ['POST'])
def search_post():
    code = request.form['Station']

    return posts(station=code)