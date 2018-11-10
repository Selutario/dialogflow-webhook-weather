#!/usr/bin/env python
# coding=utf-8

from flask import Flask, request, make_response
import os,json, re
import pyowm
import os

app = Flask(__name__)

owmapikey=os.environ.get('OWMApiKey') #or provide your key here
owm = pyowm.OWM(owmapikey)

#geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'

    return r

#processing the request from dialogflow
def processRequest(req):

    req_string = str(req)
    list_of_words = req_string.split()
    city_raw = list_of_words[list_of_words.index("{'geo-city-es':") + 1]
    city = city_raw.translate({ord(c): None for c in "'},"})
    city_country = city + ",es"


    if (city != ''):
        observation = owm.weather_at_place(city_country)
        w = observation.get_weather()
        latlon_res = observation.get_location()
        lat=str(latlon_res.get_lat())
        lon=str(latlon_res.get_lon())
        
        wind_res=w.get_wind()
        wind_speed=str(wind_res.get('speed'))
        
        humidity=str(w.get_humidity())
        
        celsius_result=w.get_temperature('celsius')
        temp_min_celsius=str(celsius_result.get('temp_min'))
        temp_max_celsius=str(celsius_result.get('temp_max'))

        speech = "Hoy en " + city + " el tiempo será el siguiente: \n" + "La temperatura estará entre "+temp_max_celsius+"ºC y "+temp_min_celsius+"ºC.\nLa humedad rondará el "+humidity+"% y la velocidad del viento "+wind_speed+" m/s"

        if (city == "Granada"):
            speech = "Me alegro que preguntes por mi ciudad natal. " + speech

    else:
        speech = "Me temo que no conozco la ciudad que indicas. Todo ha cambiado mucho desde que morí."

    return {
        "fulfillmentText": speech
        }

    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
