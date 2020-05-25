#modules 
import requests
import json
from math import radians, cos, sin, asin, sqrt 


import datetime 
import time 
import sys
import datetime as dt 
import dateutil.parser
from time import strptime
from flask import Flask
#########################

from config import Config
app = Flask(__name__)
app.config.from_object(Config)


#API urls  
bus_url = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2'
bus_stops_url = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops'
some_headers = {'AccountKey' : app.config['API_KEY']}
##############################

#global variable 
final_data = []
##############################


#functions########################## 


def testStatus(): #test LTA datamall api connection 
    
    payload = {'BusStopCode': 83139} #testing 
    r = requests.get(bus_url, params=payload, headers= some_headers)
    
    status_Code = r.status_code

    print(status_Code)
    return status_Code

testStatus()


def timeleft(arrivaltime): #display time of bus arrival 
    #bus timing (1st one)
    bustime = arrivaltime

    if len(bustime) == 0:
        timeLeft = "No service"
    else:
        d = dateutil.parser.parse(bustime)
        # print (d)

        busTime_Minute = d.strftime("%M")
        busTime_Hour = d.strftime("%H")
        # print(busTime_Hour)
        #print(busTime_Minute)

        current_Time = dt.datetime.now()

        # print (current_Time)
        currentTime_Minute = current_Time.strftime("%M")
        currentTime_Hour = current_Time.strftime("%H")
        # print (currentTime_Hour)
        #print (currentTime_Minute)

        if busTime_Hour > currentTime_Hour: 
            timeLeft = (int(busTime_Minute) + 60) - int(currentTime_Minute)
        else:
            if int(busTime_Minute) > int(currentTime_Minute):
                timeLeft = int(busTime_Minute) - int(currentTime_Minute)   
            elif int(busTime_Minute) == int(currentTime_Minute):
                timeLeft = 'Arr'
            else:
                timeLeft = str(abs(int(busTime_Minute) - int(currentTime_Minute))) + " min late"                 

    # print (timeLeft)
    return timeLeft



def current_timing(code): # to display bus timing [Chosen Bus stop] to the user 

    output_dict = {}

    payload = {'BusStopCode': code} #testing 
    r = requests.get(bus_url, params=payload, headers= some_headers)
    # print (r.url)

    if r.status_code == 200:
        output = r.json()
        services = output['Services']
        # print(services)

        for i in services:
            # print (i, '/n')

            output_dict[i['ServiceNo']] = {'NextBus' : i['NextBus'] , 'NextBus2' : i['NextBus2']}
        # print (output_dict)

        if len(output_dict) != 0: 

            header = "{0:<7} {1:^10} {2:^10}".format("Bus No", "Current", "Next")
            busString = "```\n" + header + "\n"

            for k, v in output_dict.items():
                t = timeleft(v['NextBus']['EstimatedArrival'])
                t2 = timeleft(v['NextBus2']['EstimatedArrival'])
                wc1 = v['NextBus']['Feature']
                wc2 = v['NextBus2']['Feature']

                if wc1 == "WAB":
                    wc1 = '*'
                if wc2 == "WAB":
                    wc2 = '*'

                busString = busString + "{0:<7} {1:^10} {2:^10}".format(k, str(t)+wc1, str(t2)+wc2) + "\n"
            busString = busString + "```"

        else:
            busString = "There is no more Bus Service for this Bus Stop"
        

        # buses = (json.dumps(r.json(), indent=2, sort_keys=True))
    else:
        busString = "Information is not available"

    # print (busString)
    return (busString)

current_timing(54329)


def get_BusStopNumber():
    return 


def distance(lat1, lon1, lat2, lon2): #calculation of lat and lon 
      
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 
       
    # Haversine formula  
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  
    c = 2 * asin(sqrt(a))  
     
    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371
       
    # calculate the result 
    return(c * r) 
      
      

def bus_stops(x = 0): #pip request till no data is avail  

    global final_data
    some_params =  {'$skip': x}
    r = requests.get(bus_stops_url, headers= some_headers, params = some_params)

    # print (r.url)
    # print (r.status_code)
    # print (r.text)
    a = json.dumps(r.json(), indent=2, sort_keys=True)

    # print (type(a))
    b = json.loads(a)

    data = b['value']
    final_data += data 


    # print (len(final_data))

    if len(data) != 0:
        x += 500 
        bus_stops(x)

    return final_data

# bus_stops(0)

def BusStopMsg(ls): #send bus stop details for user to choose from 
    output_dict = {} 
    for i in range(0, len(ls)):
        
        output_dict[i] = ls[i]
    # print (output_dict)

    header = "{0:<7} {1}".format("No", "Bus Stop")
    busStopString = "\n" + header + "\n"
    for k, v in output_dict.items():
        busStopString = busStopString + "{0:<7} {1}".format(k, v) + "\n"
    busStopString = busStopString 
    return (busStopString)


def calculation(lat, lon): #calculate busstop that is near user's location , arranged in order from nearest to fartheset 
    data_dict = {}
    output = {}
    data = bus_stops()
    count = 0 

    for i in data:

        data_dict[i['BusStopCode']] = {'Description': i['Description'], 'BusStopCode': i['BusStopCode'] , 'Latitude' :i['Latitude'], 'Longitude' : i['Longitude']}
        a = distance(i['Latitude'], i['Longitude'], lat, lon)

        if a < 0.5:
            output[i['BusStopCode']] = {'Description': i['Description'], 'Dist' : a}
            items = output.items()
            sorted_items = sorted(items, key=lambda key_value: key_value[1]["Dist"], reverse=False)
            final_dict = dict(sorted_items[:5]) 


    for k in final_dict.keys():
        final_dict[k].update({'Count': count})
        count += 1 

    return (final_dict)

# def calculation(lat, lon): #calculate busstop that is near user's location  
#     data_dict = {}
#     output_dict = {}
#     count = 0

#     data = bus_stops()


#     for i in data:

#         data_dict[i['BusStopCode']] = {'Description': i['Description'], 'BusStopCode': i['BusStopCode'] , 'Latitude' :i['Latitude'], 'Longitude' : i['Longitude']}

#     for k in data_dict.keys():

#         a = distance(data_dict[k]['Latitude'] , data_dict[k]['Longitude'], lat , lon) #comapre 

        
#         if a < 0.5:

#             print (a)
#             des = data_dict[k]['Description']
#             busStopNum = data_dict[k]['BusStopCode']
 
#             if count < 5:
#                 output_dict[busStopNum] = {'Description' : des , 'Count': count, 'Dist': a}
#                 count += 1

#     # print(len(output_dict))
#     # print(output_dict)
#     return (output_dict)

# calculation(1.364952 , 103.849861)


def numlist(num): #for function - GSR
	# payload = {'id':curr_id}
	
    temp ='^(' +('|'.join(num)) + ')$' 
    # print (temp)
    return (temp)


# numlist(['1','2','3','4','5','6'])