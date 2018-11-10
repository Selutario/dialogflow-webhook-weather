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

    city = req['queryResult']['parameters']['geo-city-es']
    if (city == ''):
        city = "Granada"
        
    city_country = city + ",es"
    observation = owm.weather_at_place(city_country)
    w = observation.get_weather()
    
    wind_res=w.get_wind()
    wind_speed=str(wind_res.get('speed'))
    
    humidity=str(w.get_humidity())
    
    celsius_result=w.get_temperature('celsius')
    temp_min=str(celsius_result.get('temp_min'))
    temp_max=str(celsius_result.get('temp_max'))


    if (city == "Granada"):
        introduction = "Me alegro que preguntes por mi ciudad natal. Hoy en el tiempo en la Alhambra será el siguiente: \n\n""
    elif ("" == req['queryResult']['parameters']['geo-city-es']):
        introduction = "Me temo que no conozco la ciudad que indicas. Todo ha cambiado mucho desde que morí, pero te diré el tiempo en Granada."
    else:
        introduction = "Hoy en " + city + " el tiempo será el siguiente:"

    if (temp_min == temp_max):
        temperature = "La temperatura será de " + temp_min + " grados centígrados."
    else:
        temperature = "La temperatura estará entre "+temp_min+" y " + temp_max + " grados centígrados."

    hum_wind = "La humedad rondará el " + humidity + "% y la velocidad del viento " + wind_speed + " m/s"
            
    speech = introduction + "\n\n" + temperature + hum_wind

    return {
        "fulfillmentText": speech
        }

    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
