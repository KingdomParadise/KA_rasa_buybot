import requests,re
try:
    from .data import states
except ImportError:
    from data import states



from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
 
def TEXT_ANALYZER(target_text,data_set):
    results = max([similar(str(data).lower(),str(target_text).lower())for data in data_set])
    if results>0.85:return True
    else:return False
 















vin = "XXXXXXX43AS0XXXRR"
vin = "JT4RN55R5G0222654"
vin = "JHMGE8H43AS002030"
def VIN_VALIDATOR(vin):
    print('--> VIN API CALLED')
    url = f"https://sandbox.api.kbb.com/idws/vehicle/vin/id/{vin}/?api_key=a11bf69647084057907e71f0d"
    res = requests.get(url).json()
    res = res['vinResults'] 
    # print(res[0]['makeName']) 
    if not res == []: 
        data1 = [f"{res[0]['makeName']} {res[0]['modelName']}"]
        data2 = [f"{car['trimName']}"  for car in res ]
        data=[vin]+data1+data2
        if len(data)>4:data=data[:4]
        return data
    else:
        return None

def LICENSE_PLATE_VALIDATOR(plate_number,state='CA'):
    print('--> LICENSE PLATE API CALLED')
    headers = {
        "x-rapidapi-host": "us-license-plate-to-vin.p.rapidapi.com",
        "x-rapidapi-key": "ee1de273afmsh395876c18b8894dp182de0jsn9003b89dd005",
    }
    url = "https://us-license-plate-to-vin.p.rapidapi.com/licenseplate"
    querystring = {"plate":str(plate_number),"state":state.upper()}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if 'error' in response.keys():return None
    else: 
        response = response['specifications']['vin'] 
        response = VIN_VALIDATOR(response)
        return response



def VERIFY_STATE(given_state):
    if len(given_state)==2:given_state=given_state.upper()
    else : given_state=given_state.capitalize()
    states_pool = list(states.keys()) +list(states.values()) 
    if given_state in states_pool:
        if len(given_state)==2:
            return given_state            
        else:
            state_code = [code for code,name in states.items() if name==given_state][0]
            print('State Code is ', state_code)
            return state_code
    else: return None

if __name__ == '__main__':
    # print(VIN_VALIDATOR('1C4NJPBA3GD599979'))
    print(VIN_VALIDATOR('JHMGE8H43AS002030'))
    # given_state = 'caLIFORNIA'
    # print(LICENSE_PLATE_VALIDATOR('LDWV30','fl'))
         
  