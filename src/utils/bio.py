import requests
import matplotlib.pyplot as plt
import json
import time

url = "http://162.55.40.62:8001/motion_gen/"

screenx = 1495
screeny = 562


params = {
    'screenx': screenx,
    'screeny': screeny,
    'coordinates': json.dumps([[989, 1268, 1330, 979], [447, 404, 353, 363]]), 
    'frequency': 62.5, 
    'sv': 0.4 ,
    'remove_v0': True,
    'c_delay':False,
    'key': 5163354824552418
} 


def motion():
    while True:
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                break
        except:
            pass
        
        time.sleep(1) 

    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            return "B64"
        else:
            posis = data


    results = []
    for i in range(len(posis[0])): 
        for j in range(len(posis[0][i])):  
            flag = 1 if j == len(posis[0][i])-2 else 0
            results.append(f"{round(posis[2][i][j])},{flag},{round(posis[0][i][j])},{round(posis[1][i][j])}")
    output = f'{{"mbio":"{";".join(results)};","tbio":"","kbio":""}}'

    return output