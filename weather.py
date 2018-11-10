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
#@app.route('/webhook')
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #req = "{'responseId': '39c5bf4f-eabd-4f1b-be0d-9105fdbec3e7', 'queryResult': {'queryText': 'dime el tiempo en Madrid', 'parameters': {'geo-city-es': ''}, 'allRequiredParamsPresent': True, 'fulfillmentText': 'Tiempo no disponible.', 'fulfillmentMessages': [{'text': {'text': ['Tiempo no disponible.']}}], 'intent': {'name': 'projects/boabdil-545a0/agent/intents/aa02d570-b786-4c63-8ef5-a562e91ab49d', 'displayName': 'Cortesía - Tiempo'}, 'intentDetectionConfidence': 1.0, 'languageCode': 'es'}, 'originalDetectIntentRequest': {'payload': {}}, 'session': 'projects/boabdil-545a0/agent/sessions/05bcd830-a89f-0141-6d64-6cf6fb1c8e78'}"

    print("Request:")
    print(json.dumps(req, indent=4))
    
    res = processRequest(req)
    res = json.dumps(req, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#processing the request from dialogflow
def processRequest(req):

    list_of_words = req.split()
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
        speech = "Me temo que no conozco la ciudad que indicas. Todo ha cambiado mucho desde que yo morí."

    return {
        "speech": speech,
        "displayText": speech,
        "source": "dialogflow-weather-by-satheshrgs"
        }

    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')
