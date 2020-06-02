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
    def get_results(cleaned_station, r=None):

        if not r:
            r = requests.get(f'http://api.rtt.io/api/v1/json/search/{cleaned_station}', auth=(os.environ.get('rtt_uname'), os.environ.get('rtt_pword')))
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
            train['UID'] = service['serviceUid']
            rundate = service['runDate'].split('-')
            
            train['year'] = rundate[0]
            train['month'] = rundate[1]
            train['day'] = rundate[2]

            trains.append(train)
        print(trains, file=sys.stderr)
        return render_template('depboard.html', station=name, trains=trains)

    # return render_template('search.html')

    # Check if looks like CRS
    if re.search("^[A-Za-z]{3}$", station):
        for location in setup.location_dict:
            if re.search(f'^({station})$', location['CRS'], re.IGNORECASE):
                
                return get_results(location['CRS'])
    if re.search("^[A-Za-z]*$", station):
        for location in setup.location_dict:
            if re.search(f'^({station})$', location['TIPLOC'], re.IGNORECASE) or re.search(f'^({station})$', location['DESC'], re.IGNORECASE):
                return get_results(location['CRS'])
    if re.search("^[A-Za-z\s]*$", station):

        for location in setup.location_dict:
            if re.search(f'^({station})$', location['DESC'], re.IGNORECASE):
                # print(location, file=sys.stderr)
                return get_results(location['CRS'])
        possible_matches = []
        for location in setup.location_dict:
            if re.search(f'^.*({station}).*$', location['DESC'], re.IGNORECASE):
                possible_matches.append(location)
        if len(possible_matches)==0:
            return render_template('search.html')
        if len(possible_matches)==1:
            return get_results(possible_matches[0]['TIPLOC'])
        if len(possible_matches)<1000:
            return render_template('matches.html', matches=possible_matches)
    return render_template('search.html')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search', methods = ['POST'])
def search_post():
    code = request.form['Station']

    return posts(station=code)


@app.route('/train')
@app.route('/train/<train_id>/<year>/<month>/<day>')
def train(train_id=None, year=None, month=None, day=None):
    r = requests.get(f'http://api.rtt.io/api/v1/json/service/{train_id}/{year}/{month}/{day}', auth=(os.environ.get('rtt_uname'), os.environ.get('rtt_pword')))
    result = r.json()
    identity = result['trainIdentity']
    origins = []
    destinations = []

    for origin in result['origin']:
        origins.append(origin['publicTime'] + ' ' + origin['description'])

    origins_str = ' & '.join(origins)

    for destination in result['destination']:
        destinations.append(destination['description'] + ' ' + destination['publicTime'])

    destinations_str = ' & '.join(destinations)

    train_header = f'{identity} {origins_str} to {destinations_str}'

    calling_points = []

    for location in result['locations']:
        calling_point = {}
        calling_point['location_desc'] = location['description']
        calling_point['tiploc'] = location['tiploc']
        calling_point['booked_arr'] = location['gbttBookedArrival'] if 'gbttBookedArrival' in location.keys() else ''
        calling_point['booked_dep'] = location['gbttBookedDeparture'] if 'gbttBookedDeparture' in location.keys() else ''
        calling_point['expected_arr'] = location['realtimeArrival'] if 'realtimeArrival' in location.keys() else ''
        calling_point['expected_dep'] = location['realtimeDeparture'] if 'realtimeDeparture' in location.keys() else ''
        calling_point['arr_act'] = location['realtimeArrivalActual'] if 'realtimeArrivalActual' in location.keys() else 'false'
        calling_point['dep_act'] = location['realtimeDepartureActual'] if 'realtimeDepartureActual' in location.keys() else 'false'
        calling_points.append(calling_point)



    return render_template('train.html', train_header=train_header, calling_points=calling_points)

    