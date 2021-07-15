import requests,re

vin = "XXXXXXX43AS0XXXRR"
vin = "JT4RN55R5G0222654"
vin = "JHMGE8H43AS002030"
def VIN_VALIDATOR(vin):
    print('--> VIN API CALLED')
    url = f"https://sandbox.api.kbb.com/idws/vehicle/vin/id/{vin}/?api_key=a11bf69647084057907e71f0d"
    res = requests.get(url).json()['vinResults']
    if not res == []:
        data = res[0] 
        data={
            "vehicleId":data['vehicleId'],
            "vehicleName":data['vehicleName'],
            "yearId":data['yearId'],
            "makeName":data['makeName'],
            "modelName":data['modelName'],
            "doors":data['doors'],
        }

        text=''  
        for val in data:
            text+=f'{val}: { data[val]}, \n'
        return text
    else:
        return None

def LICENSE_PLATE_VALIDATOR(plate_number):
    print('--> LICENSE PLATE API CALLED')
    headers = {
        "x-rapidapi-host": "us-license-plate-to-vin.p.rapidapi.com",
        "x-rapidapi-key": "ee1de273afmsh395876c18b8894dp182de0jsn9003b89dd005",
    }
    url = "https://us-license-plate-to-vin.p.rapidapi.com/licenseplate"
    querystring = {"plate":str(plate_number),"state":"CA"}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if 'error' in response.keys():return None
    else:
        response = response['specifications']
        text=''  
        for val in response:
            text+=f'{val}: { response[val]}, \n' 
        return text



if __name__ == '__main__':
     print(LICENSE_PLATE_VALIDATOR('22r'))
 
# text = '+92 3167815639  +92 3167815639  '
# phone_numbers = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', text)

# print(phone_numbers)
 