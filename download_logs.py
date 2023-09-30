import pandas as pd
import requests
from requests.packages import urllib3
from datetime import datetime
import os
import pathlib
import logging
from PyQt5.QtWidgets import QErrorMessage, QMessageBox
import range_regex
import vglobals
import tqdm
from time import sleep

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))

def createut(datetimestr): #02/10/2020 21:35
    datetimeformat = datetime.strptime(datetimestr, "%d/%m/%Y %H:%M")
    unixformat = datetime.timestamp(datetimeformat)
    unixformat = int(unixformat)
    return unixformat  #1601685300

def createdt(unixtimestr): #1601685300
    if int:
        dt = datetime.fromtimestamp(unixtimestr / 1e3)
        datetimestamp = dt.strftime("%d/%m/%Y %H:%M")
        return datetimestamp #02/10/2020 21:35
    else:
        datetimestamp = unixtimestr.strftime("%d/%m/%Y %H:%M")
        return datetimestamp #02/10/2020 21:35

def createaddr(startdt, enddt): #'02/10/2020 21:35', '02/10/2020 22:35'
    protocol = 'https://'
    ip = '10.0.38.42'
    request = '/Olog/resources/logs?'
    startDatestr = 'start='
    endDatestr = '&end='
    start = createut(startdt)
    end = createut(enddt)
    addressstr = protocol + ip + request + startDatestr + str(start) + endDatestr + str(end)
    return addressstr #https://10.0.38.42/Olog/resources/logs?start=1565654400&end=1566777599

def dorequest(startdt, enddt): #'02/10/2020 21:35', '02/10/2020 22:35'
    address = createaddr(startdt, enddt)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    with requests.get(address, verify=False, stream=True) as r:#.json()
        response_length = len(r.content)
        chunk_length = 0
        for chunk in r.iter_content(chunk_size=1024):
            if (response_length - len(chunk)) > 0:
                chunk_length += len(chunk)
                vglobals.global_progressBarVal = int((chunk_length / response_length)*50)
                sleep(0.001)
            else:
                r.close
    jsonfile = r
    r.close()
    return jsonfile.json()

def downloaddata(startdt, enddt, fS): #'02/10/2020 21:35', '02/10/2020 22:35'
    r = dorequest(startdt, enddt)
    logdict =	{
        "id": "",
        "createdDate": "",
        "eventStart": "",
        "logbook": "",
        "tag": "",
        "description": ""
        }
    
    logdictlist = []
    x = 0
    actual = vglobals.global_progressBarVal
    if fS.doFilter == True:
        total = 30
    else:
        total = 50

    for i in r:
        vglobals.global_progressBarVal = actual + int((x/len(r))*total)
        dict_r = i
        list_r = []
        for i in dict_r:
            ilist = []
            if i == 'id':
                logdict["id"] = dict_r[i]
            if i == 'version':
                logdict["id"] = str(logdict["id"]) + "_" + str(dict_r[i])
            if i == 'createdDate':
                logdict["createdDate"] = createdt(dict_r[i])
            if i == 'eventStart':
                logdict["eventStart"] = createdt(dict_r[i])
            if i == 'logbooks':
                aux_list = []
                auxstr = ''
                aux = dict_r[i] #pares keys-values das tags, conforme aparecem no log
                if aux: #se aux não estiver vazia
                    #print('is not empty')
                    if len(aux) == 1: #se o tamanho de aux for igual a 1
                        for i in aux: #para cada índice em aux
                            logdict["logbook"] = i['name'] #logdict da key tag recebe o valor de dict_r[i]
                    else: #senão
                        for i in aux:
                            aux_list.append(i['name'])
                            if not auxstr:
                                auxstr = auxstr + i['name']
                            else:
                                auxstr = auxstr + '/' + i['name']
                            logdict["logbook"] = auxstr #aux_list
                else:
                    logdict["logbook"] = ''
            if i == 'tags':
                aux_list = []
                auxstr = ''
                aux = dict_r[i] #pares keys-values das tags, conforme aparecem no log
                if aux: #se aux não estiver vazia
                    #print('is not empty')
                    if len(aux) == 1: #se o tamanho de aux for igual a 1
                        for i in aux: #para cada índice em aux
                            logdict["tag"] = i['name'] #logdict da key tag recebe o valor de dict_r[i]
                    else: #senão
                        for i in aux:
                            aux_list.append(i['name'])
                            if not auxstr:
                                auxstr = auxstr + i['name']
                            else:
                                auxstr = auxstr + '/' + i['name']
                            logdict["tag"] = auxstr #aux_list
                else:
                    logdict["tag"] = ''
            if i == 'description':
                logdict["description"] = dict_r[i]
        logdictlist.append(logdict.copy())
        x += 1
    df = pd.DataFrame(logdictlist)
    if fS.doFilter == True:
        df = handle_data(df, fS)
    createXLS(df)
    vglobals.global_progressBarVal = 100
    #return logdictlist

def handle_data(df, fS):
    dataFrame = df
    #if not fS:
    dataFrame = filter_ID(dataFrame, fS)
    dataFrame = filter_Description(dataFrame, fS)
    dataFrame = filter_Logbook(dataFrame, fS)
    dataFrame = filter_Tag(dataFrame, fS)
    return dataFrame

def filter_ID(df, fS):
    if fS.leID != '':
        leID_list = fS.leID
        #ID_list = list(range(min(leID_list),max(leID_list)))
        regexPattern = range_regex.range_regex.regex_for_range(min(leID_list), max(leID_list))
        dfFilter = df.id.str.contains(regexPattern)
        df = df[dfFilter]
        vglobals.global_progressBarVal = vglobals.global_progressBarVal + 5
    else:
        vglobals.global_progressBarVal = vglobals.global_progressBarVal + 5
    return df

def filter_Description(df, fS):
    aux = vglobals.global_progressBarVal
    if fS.leDescription != '':
        for i in range(len(fS.leDescription)):
            df = df[df['description'].str.contains(fS.leDescription[i], na=False, case=0)]
            vglobals.global_progressBarVal = aux + int((i/len(fS.leDescription))*5)
            sleep(0.001)
    else:
        vglobals.global_progressBarVal = vglobals.global_progressBarVal + 5
    return df

def filter_Logbook(df, fS):
    if fS.leLogbook != '':
        aux = vglobals.global_progressBarVal
        for i in range(len(fS.leLogbook)):
            df = df[df['logbook'].str.contains(fS.leLogbook[i], na=False, case=0)]
            vglobals.global_progressBarVal = aux + int((i/len(fS.leLogbook))*5)
            sleep(0.001)
    else:
        vglobals.global_progressBarVal = vglobals.global_progressBarVal + 5
    return df

def filter_Tag(df, fS):
    if fS.leTag != '':
        aux = vglobals.global_progressBarVal
        for i in range(len(fS.leTag)):
            df = df[df['tag'].str.contains(fS.leTag[i], na=False, case=0)]
            vglobals.global_progressBarVal = aux + int((i/len(fS.leTag))*5)
            sleep(0.001)
    else:
        vglobals.global_progressBarVal = vglobals.global_progressBarVal + 5
    return df

def createXLS(df):
    FILE = os.path.join(THIS_FOLDER, 'logs.xls')
    try:
        df.to_excel(FILE, sheet_name='Logs', index=False)
    except:
        error_dialog = QErrorMessage()
        error_dialog.showMessage('Error creating XLS file!')
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()