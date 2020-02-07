import json
import requests 

import time
from timeloop import Timeloop
from datetime import timedelta

RPS_Server=Timeloop()


base_url = "http://3.6.79.236/"
rps_username='racenergy'
rps_password='rac1234'

def entry_id(json):
    try:
        return json['entry_id']
    except KeyError:
        return 0



def getAuthToken(userName,password):
    URL=base_url+"api-token-auth/"
    payload={'username':userName,'password':password}
    header = {"content-type": "application/json"}

    try:
        response= requests.post(URL,data=json.dumps(payload), headers=header, verify=False)

        r_json =response.json()
        # print("############: ",r_json)


        if len(r_json['token'])!=0:

            return r_json['token']

    except Exception as e:

        return None


def getLatestEntry():
    URL = base_url+"get-latest-entry/"
    token = getAuthToken(rps_username,rps_password)


    header = {"content-type": "application/json",'Authorization':'Token '+token}

    response=requests.get(URL, headers=header, verify=False)
    r_json =response.json()
    # print("############: ",r_json)

    return r_json['last_entry']


def makeLatestJsonData(fileName):
    with open(fileName) as f:
        data = json.load(f)

    data.sort(key=entry_id,reverse=True)
    last_entry_id = getLatestEntry()

    print("### Latest Enter: ",last_entry_id)
    temp_data = []
    for json_obj in data:

        if json_obj['entry_id']==last_entry_id:
            break
        elif json_obj['entry_id']>last_entry_id:
            temp_data.append(json_obj)

    # print(temp_data)
    return temp_data

def send_json_to_server(json_arr):
    URL = base_url+"upload-rps-data/"
    token = getAuthToken(rps_username,rps_password)
    json_arr.sort(key=entry_id,reverse=False)

    header = {"content-type": "application/json",'Authorization':'Token '+token}

    try:
        response=requests.post(URL,data=json.dumps(json_arr),headers=header, verify=False)
        print('######## Response: ',response)
        r_json =response.json()
        print("############: ",r_json)

        return r_json['status']
    except Exception as e:
        print("[ERROR]",e)
        return {}


def jsonData_CS_server(fileName):

    json_to_send=makeLatestJsonData(fileName)

    json_arr_len=len(json_to_send)
    print("##### Length of Json Array: ",json_arr_len)


    if json_arr_len>0:
        status=send_json_to_server(json_to_send)
        print("## Status: ",status)



@RPS_Server.job(interval=timedelta(seconds=60))
def run_RPS():

    jsonData_CS_server('/home/ubuntu/rpsServer/sample.json')
    


if __name__=='__main__':
    RPS_Server.start(block=True)


# jsonData_CS_server('/home/ubuntu/rpsServer/sample.json')
