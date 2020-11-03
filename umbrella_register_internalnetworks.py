# Script Desenvolvido por: Valentim Uliana
# Script que cria Internal Networks no Umbrella a partir de um CSV, facilitando para cadastro de redes em massa.


import json
import requests
import configparser
import csv
import sys
import ipaddress
import os.path
from collections import OrderedDict

# Arquivo de configuração
config = configparser.ConfigParser()
config.read('config')
org_id = config['Umbrella']['OrgID']
mgmt_api_key = config['Umbrella']['ManagementAPIKey']
mgmt_api_secret = config['Umbrella']['ManagementAPISecret']


#Headers
header_sites = {'organizationID': '{}'.format(org_id)}
header_internalnet = {'organizationID': '{}'.format(org_id),'Content-Type': 'application/json','Accept': 'application/json'}

# management api url, usado para pegar o access token do reporting api
mgmt_url = 'https://management.api.umbrella.com/v1'


#Função para fazer GET das Internal Networks existentes no Umbrella
def get_internalnetworks_request(endpoint):
    r = requests.get(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret))
    body = json.loads(r.content)
    return body

#Função para fazer GET dos sites
def get_sites_request(endpoint):
    r = requests.get(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret))
    body = json.loads(r.content)
    return body

#Função para fazer POST e criar um novo Site
def post_site_request(endpoint, sites):
    r = requests.post(mgmt_url+endpoint, headers=header_sites, auth=(mgmt_api_key, mgmt_api_secret), data=sites)
    body = json.loads(r.content)
    return body


#Função para fazer POST e criar as Internal Networks
def post_internalnetworks_request(endpoint, internalnetworks, nome):
    r = requests.post(mgmt_url+endpoint, headers=header_internalnet, auth=(mgmt_api_key, mgmt_api_secret), data=internalnetworks)
    
    if r.status_code == 200:
        print("Internal Network:", nome + " foi cadastrada com sucesso")

    body = json.loads(r.content)
    return body

# Função pra checar se no CSV tem algum IpNetowrk inválido
def checkValidIpNetwork(ip, name):
    try:
        ipaddress.IPv4Network(ip)
        return True
    except ValueError:
        print('Ip/netmask inválido para o IPv4:', ip + ", Internal Network Name:", name)
        return False

# Função para remover duplicados no CSV 
def removeduplicate(it):
    seen = set()
    for x in it:
        t = tuple(x.items())
        if t not in seen:
            yield x
            seen.add(t)

# Função para checar se valor inserido no SiteID é inteiro
def getIntSiteID():
    while True:
        number = input("Digite o Id do Site que deseja atribuir: ")
        if number.isdigit():
            return number


def main():
    # variavel pra checkar se um site ja esta cadastrado
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

    csvfile = input("Digite o nome do csv que voce vai atribuir: ")

    if os.path.isfile(csvfile.strip() + ".csv"):
        pass
    else:
        print ("\nArquivo", csvfile + ".csv " + "não encontrado")
        sys.exit()

    # Abrir o CSV se existe
    f = open(csvfile.strip() + ".csv", 'r',encoding='utf-8-sig')  

    # Adicionar as colunas no output do CSV para ficar igual JSON pra post.
    reader = csv.DictReader( f, fieldnames = ("name","ipAddress","prefixLength"))  

    
    #Odernar o Csv para nao ter problemas futuros no umbrela  
    sorted_csv = sorted(reader, key=lambda row: (row['name']))
    
    # Fazer o Parse de CSV para JSON  
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
        print("\nVerifique os Ip's acima em seu CSV, pois eles não são válidos! Após arrumar, rode o script novamente =D")
        sys.exit()
    
    
    # Loop para opção, só sao quando for uma opçao válida
    while True:
        try:
            opcao = int(input("Você deseja criar um site novo ou atribuir o csv à um existente? (1 - criar, 2 - atribuir): "))
        except ValueError:
            print("Digite somente numeros.")
            continue
        
        #Só fazer o get se deseja criar um novo site
        if opcao == 1:
            #fazer o get dos sites para pegar verificar se o nome que vc deu pro site já existe
            r_get_sites_check = get_sites_request('/organizations/{}/sites'.format(org_id))
            dump_sites_check = json.dumps(r_get_sites_check)
            sites_json_check = json.loads(dump_sites_check)
              
        
        if opcao > 2 or opcao == 0:
            print("Opção inválida. Digite 1 para criar um novo site ou 2 para atribuir o csv à um site existente")
            continue
        else:
            break

    if opcao == 1:
        site_name = input("Digite o nome do Site: ")
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
            print("\nSite já foi cadastrado, por favor digite um nome que não esteja cadastrado")
            sys.exit()
    
    elif opcao == 2:
        #fazer o get dos sites para pegar os id
        r_get_sites = get_sites_request('/organizations/{}/sites'.format(org_id))
        dump_sites = json.dumps(r_get_sites)
        sites_json = json.loads(dump_sites)
        listasites = ""
        for sites in sites_json:
            listasites += "Site: " + sites['name'] + ", ID: " + str(sites['siteId']) + "\n"
            #print(sites['name'])  
        print(listasites)
        existente = True

    # Remover duplicados exatos do csv e criar nova lista adionando somente o que não é duplicado
    lista_removido_duplicado = []
    for item in removeduplicate(new_internalnet):
        lista_removido_duplicado.append(item)
    
    #Remover nomes iguais dentro da lista de removido_duplicado, pois se tem mais de um nome igual já no csv, mantem o primeiro e remove o resto
    lista_final_new = list()
    items_set = set()    
    for js in lista_removido_duplicado:
        # só adiciona items nao vistos (referenciando to 'nome' como key)
        if not js['name'] in items_set:
            # marcar como seen
            items_set.add(js['name'])         
            # add to results
            lista_final_new.append(js)

    #Remover Ip/prefix iguais dentro da lista de removido_duplicado, pois se tem mais de um um ip/prefix igual já no csv, mantem o primeiro e remove o resto
    lista_final = list()
    items_set_ip = set()
    for ip in lista_final_new:
        # só adiciona items nao vistos (referenciando to 'ipddress/prefix' como key)
        ipnet = ip['ipAddress'] + "/" + str(ip['prefixLength'])
        if not ipnet in items_set_ip:
            # marcar como seen
            items_set_ip.add(ipnet)          
            # adciona a lista final
            lista_final.append(ip)

    #Comparar o nome e ippadress que tem no CSV com o que já tem no Umbrella, e cadastrar só os que nao tem! 
    #As comparações anteriores foram todas para o arquivos do CSV, ou seja, localmente
    for k in range(len(act_internal_net)):
        for i in range(len(lista_final)):
            ipatual = act_internal_net[k]['ipAddress'] + "/" + str(act_internal_net[k]['prefixLength'])
            ipnovo =  lista_final[i]['ipAddress'] + "/" + str(lista_final[i]['prefixLength'])

            if (act_internal_net[k]["name"] == lista_final[i]['name'] or ipatual == ipnovo):
                lista_final.pop(i)              
                break   
       
    #Se a lista retornar vazia não cadastrar nada
    if not lista_final:
        print("Nada neste CSV para adicionar!! Provalemente o que tem no CSV, já está cadastrado no Umbrella!!!")
    else:
        # if para saber se a opcao é pra adicionar à um site existente
        if existente == True:
            new_siteId = getIntSiteID()
            for cadastrar in lista_final:
                #Atribui o siteID escolhido ao final da lista Json que vai mandar o POST
                cadastrar['siteId'] = new_siteId 
                post_internalnetworks_request('/organizations/{}/internalnetworks'.format(org_id), json.dumps(cadastrar), cadastrar['name'])             
        else:
            for cadastrar in lista_final:
                #Adiciona o siteID criado ao final da lista Json que vai mandar o POST
                cadastrar['siteId'] = siteId
                post_internalnetworks_request('/organizations/{}/internalnetworks'.format(org_id), json.dumps(cadastrar), cadastrar['name'])

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n\nFechando script...\n\n")
        sys.stdout.flush()
        pass
     