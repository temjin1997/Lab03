import requests
import json
import re
from pprint import pprint

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

switchuser = 'cisco'
switchpass = 'cisco'

################## GET CDP Nei by NX-API CLI ##################
url = "https://10.50.50.19/ins"

myheaders = {
  #'Accpet': 'application/yang-data+json',
  'Content-Type': 'application/json'
  #'Authorization': 'Basic Y2lzY286Y2lzY28='
}

payload = {
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "sid",
    "input": "show cdp nei",
    "output_format": "json"
  }
}

response = requests.post(url, headers=myheaders, data=json.dumps(payload), auth=(switchuser,switchpass), verify=False).json()
#print(response)

################## POST Login with NX-API REST ##################
auth_url = "https://10.50.50.19/api/mo/aaaLogin.json"
auth_body={"aaaUser":{"attributes":{
      "name":switchuser,"pwd":switchpass}}}

auth_response = requests.post(auth_url, data=json.dumps(auth_body), timeout=5, verify=False).json()
token = auth_response['imdata'][0]['aaaLogin']['attributes']['token']
cookies = {}
cookies['APIC-cookie']=token
#print(cookies)

counter = 0
nei_count = int(response['ins_api']['outputs']['output']['body']['neigh_count'])
#print(nei_count)

################## POST update interface description with NX-API REST ##################
while counter < nei_count:
  hostname = response['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info'][counter]['device_id']
  local_int = response['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info'][counter]['intf_id']
  remote_int = response['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info'][counter]['port_id']
  
  body = {
    "l1PhysIf": {
      "attributes": {
        "descr": "Connected to "+hostname+"-"+remote_int
      }
    }
  }
  counter += 1

  if local_int !='mgmt0':
    int_name = str.lower(str(local_int[:3]))
    int_num = re.search(r'[1-9]/[1-9]*',local_int)
    int_url = 'https://10.50.50.19/api/mo/sys/intf/phys-['+int_name+str(int_num.group(0))+'].json'
    post_response = requests.post(int_url, data=json.dumps(body), headers=myheaders, cookies=cookies, verify=False).json()
    print(post_response)

