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

    city_raw = req['queryResult']['parameters']['geo-city-es']
    city = city_raw
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


    if (city_raw == "Granada"):
        introduction = "Me alegro que preguntes por mi ciudad natal. Ahora mismo el tiempo en la Alhambra es el siguiente: "
    else:
        introduction = "Hoy en " + city + " el tiempo es el siguiente:"

    if (temp_min == temp_max):
        temperature = "La temperatura ronda los " + temp_min + " grados. "
    else:
        temperature = "La temperatura está entre los "+temp_min+" y los " + temp_max + " grados. "

    hum_wind = "La humedad está en torno al " + humidity + "% y la velocidad del viento " + wind_speed + " m/s"


    if (city_raw != ""):        
        speech = introduction + "\n\n" + temperature + hum_wind
    else:
        speech = "Me temo que no conozco la ciudad que indicas. Todo ha cambiado mucho desde que morí."

    return {
        "fulfillmentText": speech
        }

    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
