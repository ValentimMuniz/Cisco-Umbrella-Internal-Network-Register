# Copyright (C) 2020  Valentim Uliana

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
 
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
 
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/# Copyright (C) 2020 Valentim Uliana

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
 
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
 
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/


import json
import requests
import configparser
import csv
import sys
import ipaddress
import os.path
from collections import OrderedDict

# Parsing the config file
config = configparser.ConfigParser()
config.read('config')
org_id = config['Umbrella']['OrgID']
mgmt_api_key = config['Umbrella']['ManagementAPIKey']
mgmt_api_secret = config['Umbrella']['ManagementAPISecret']


#Headers
header_sites = {'organizationID': '{}'.format(org_id)}
header_internalnet = {'organizationID': '{}'.format(org_id),'Content-Type': 'application/json','Accept': 'application/json'}

# management api urli
mgmt_url = 'https://management.api.umbrella.com/v1'


#Function to GET Internal Networks in Umbrella
def get_internalnetworks_request(endpoint):
    r = requests.get(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret))
    body = json.loads(r.content)
    return body

#Funtion to GET Umbrella Sites
def get_sites_request(endpoint):
    r = requests.get(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret))
    body = json.loads(r.content)
    return body

#Function to POST a new Site
def post_site_request(endpoint, sites):
    r = requests.post(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret), data=sites)
    body = json.loads(r.content)
    return body


#Function to POST a new Internal Network
def post_internalnetworks_request(endpoint, internalnetworks, nome):
    r = requests.post(mgmt_url+endpoint, headers=header_internalnet, auth=(mgmt_api_key, mgmt_api_secret), data=internalnetworks)
    
    if r.status_code == 200:
        print("Internal Network:", nome + " was successfuly registred")

    body = json.loads(r.content)
    return body

#Function to check if has a Invalid IpNetword in CSV
def checkValidIpNetwork(ip, name):
    try:
        ipaddress.IPv4Network(ip)
        return True
    except ValueError:
        print('Invalid Ip/netmask fo IPv4:', ip + ", Internal Network Name:", name)
        return False

# Function to remove exactly duplicates in CSV
def removeduplicate(it):
    seen = set()
    for x in it:
        t = tuple(x.items())
        if t not in seen:
            yield x
            seen.add(t)

# Function to check if the the value given for SiteID is int
def getIntSiteID():
    while True:
        number = input("Type the SiteID that you want assign: ")
        if number.isdigit():
            return number


def main():
    # variable the check if a site is already registred
    cadastrado = False
    # fazer o get das internal netwokrs para comparar com o vsv
    r_get_internalnet = get_internalnetworks_request('/organizations/{}/internalnetworks'.format(org_id))
    
    #Tratar json de r_get_internalnet
    dump_actual_internalnet = json.dumps(r_get_internalnet)
    act_internal_net = json.loads(dump_actual_internalnet)
    
    # remover do json act_internal_net o que nao importa comparar
    for element in act_internal_net: 
        del element['originId']
        del element['siteName']
        del element['createdAt']
        del element['modifiedAt']
        del element['siteId']

    csvfile = input("Type the name of CSV that you want use: ")

    if os.path.isfile(csvfile.strip() + ".csv"):
        pass
    else:
        print ("\nArchive", csvfile + ".csv " + "not found")
        sys.exit()

    # Open the CSC
    f = open(csvfile.strip() + ".csv", 'r',encoding='utf-8-sig')  

    # Adding columns to CSV
    reader = csv.DictReader( f, fieldnames = ("name","ipAddress","prefixLength"))  

    
    #Sorting the CSV by Name
    sorted_csv = sorted(reader, key=lambda row: (row['name']))
    
    #Parse the CSV
    dump_new_internalnet = json.dumps( [ row for row in sorted_csv ])  
    new_internalnet = json.loads(dump_new_internalnet)
    
    count = 0
    for net in new_internalnet:
        check = checkValidIpNetwork(net['ipAddress'] + "/" + net['prefixLength'], net['name'])
        if check == False:
            count+=1
        else:
            pass

    if count > 0:
        print("\nCheck the Ip's above in your CSV, they are not valid! After fixing, run the script again =D")
        sys.exit()
    
    
    # Loop for option
    while True:
        try:
            opcao = int(input("Do you want to create a new Site or assign csv to an existing one? (1 - create, 2 - assign): "))
        except ValueError:
            print("Type numbers only.")
            continue
        
        #Only do GET if option is create a new one
        if opcao == 1:
            #fazer o get dos sites para pegar verificar se o nome que vc deu pro site já existe
            r_get_sites_check = get_sites_request('/organizations/{}/sites'.format(org_id))
            dump_sites_check = json.dumps(r_get_sites_check)
            sites_json_check = json.loads(dump_sites_check)
              
        
        if opcao > 2 or opcao == 0:
            print("Invalid option. Enter 1 to create a new Site or 2 to assign csv to an existing Site")
            continue
        else:
            break

    if opcao == 1:
        site_name = input("Type the Site name: ")
        for ja_cadastrado in sites_json_check:
            if ja_cadastrado['name'] == site_name:
                cadastrado = True
                break
        if cadastrado == False:
            payload = {'name': site_name}
            r_site = post_site_request('/organizations/{}/sites'.format(org_id), payload)
            siteId = r_site['siteId']
            existente = False
        else:
            print("\nSite has already been registered, please enter a name that is not registered")
            sys.exit()
    
    elif opcao == 2:
        #Get Sites ID
        r_get_sites = get_sites_request('/organizations/{}/sites'.format(org_id))
        dump_sites = json.dumps(r_get_sites)
        sites_json = json.loads(dump_sites)
        listasites = ""
        for sites in sites_json:
            listasites += "Site: " + sites['name'] + ", ID: " + str(sites['siteId']) + "\n"
            #print(sites['name'])  
        print(listasites)
        existente = True

    # Remove exact duplicates from the csv and create a new list adding only what is not duplicated
    lista_removido_duplicado = []
    for item in removeduplicate(new_internalnet):
        lista_removido_duplicado.append(item)
    
    
    #Remove identical names within the list of removed_duplicate, because if you have more than one equal name already in csv, keep the first one and remove the rest
    lista_final_new = list()
    items_set = set()    
    for js in lista_removido_duplicado:
        # só adiciona items nao vistos (referenciando to 'nome' como key)
        if not js['name'] in items_set:
            # mark as seen
            items_set.add(js['name'])         
            # add to lista_final_new
            lista_final_new.append(js)

    #Remove the same Ip / prefix within the  lista_removido_duplicado list, because if you have more than one equal ip/prefix in the csv, keep the first one and remove the rest
    lista_final = list()
    items_set_ip = set()
    for ip in lista_final_new:
        ipnet = ip['ipAddress'] + "/" + str(ip['prefixLength'])
        if not ipnet in items_set_ip:
            # Mark as seen
            items_set_ip.add(ipnet)          
            # Add to lista_final
            lista_final.append(ip)

    
    #Compare the name and ippadress you have in CSV with what you already have in Umbrella, and register only those you don't have!
    #The previous comparisons were all for the CSV files, that is, locally
    for k in range(len(act_internal_net)):
        for i in range(len(lista_final)):
            ipatual = act_internal_net[k]['ipAddress'] + "/" + str(act_internal_net[k]['prefixLength'])
            ipnovo =  lista_final[i]['ipAddress'] + "/" + str(lista_final[i]['prefixLength'])

            if (act_internal_net[k]["name"] == lista_final[i]['name'] or ipatual == ipnovo):
                lista_final.pop(i)              
                break   
       
    #If the list is empty, do nothing
    if not lista_final:
        print("Nothing in this CSV to register !! Probably what you have on CSV, you are already registered on Umbrella !!!")
    else:
        # A codintion to check if optin is for adding the CSV values to a Site that exists
        if existente == True:
            new_siteId = getIntSiteID()
            for cadastrar in lista_final:
                cadastrar['siteId'] = new_siteId 
                post_internalnetworks_request('/organizations/{}/internalnetworks'.format(org_id), json.dumps(cadastrar), cadastrar['name'])             
        else:
            for cadastrar in lista_final:
                cadastrar['siteId'] = siteId
                post_internalnetworks_request('/organizations/{}/internalnetworks'.format(org_id), json.dumps(cadastrar), cadastrar['name'])

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n\nClosing script...\n\n")
        sys.stdout.flush()
        pass
     
