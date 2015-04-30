import requests
from bs4 import BeautifulSoup as bs
import time
from pymongo import MongoClient
import dbConfig as dbc

middles={}
middles['APELAX']= [104, 110, 111, 115, 116, 118, 119, 122, 131, 132, 133]
middles['APECHI']= [100, 101, 102, 103, 105, 106, 107, 108, 109, 112, 113, 114, 117, 120, 121, 123, 124, 125, 126, 127, 128, 129, 130, 134]
mdb=dbc.init_db('test','test')


def getTracks(middle_start, middle_end, start=1, end=2, countThres=50, chunkSize=3, timesleep=1):
    for middle in range(middle_start, middle_end):
        if middle in middles['APELAX']:
            prefix='APELAX'
        elif middle in middles['APECHI']:
            prefix='APECHI'
        else:
            continue
        
        countNoExist=0
        chunks=[]
        
        for i in range(start, end):
            if countNoExist>=countThres:
                break
            
            time.sleep(timesleep)
            trackNumber='%s%03d%07d' %(prefix, middle, i)
            param={}
            param['lang']='zh'
            param['trackingno']=trackNumber
            info = getSingleTrackInfo(param)
            
            #check if no more number available
            if info['code']==200:
                if len(info['detail'])==0:
                    countNoExist+=1
                else:
                    countNoExist=0
            else:
                countNoExist+=1
            
            chunks.append(info)
            if len(chunks)>=chunkSize:
                dbresult=mdb.insert_many(chunks)
                print dbresult.inserted_ids
                chunks=[]
        dbresult=mdb.insert_many(chunks)
        print dbresult.inserted_ids


def getSingleTrackInfo(param):
    ret={}
    ret['_id']=param['trackingno'][6:]
    ret['base']=param['trackingno'][:6]
    ret['middle']=param['trackingno'][6:9]
    r = requests.get("https://www.ecmsglobal.com/oms/showtracking", params=param)
    if r.status_code==200:
        res_list=[]
        text= bs(r.text)
        dls=text.findAll("dl", class_="trackList")
        if len(dls)>0:
            dds=dls[0].findAll("dd")
            if len(dds)>0:
                for dd in dds:
                    res={}
                    divn=dd.findAll("div", class_="n")
                    if len(divn)>0:
                        trackStatus=divn[0].contents[0]
                        res['status']=trackStatus
                    else:
                        continue
                    divw=dd.findAll("div", class_="w")
                    if len(divw)>0:
                        if len(divw[0].contents)>0:
                            trackLoca=divw[0].contents[0]
                        else:
                            trackLoca=''
                        res['location']=trackLoca
                    else:
                        continue
                    divt=dd.findAll("div", class_="t")
                    if len(divt)>0:
                        trackTime=divt[0].contents[0]
                        res['time']=trackTime
                    else:
                        continue
                    res_list.append(res)
        ret['code']=200
        ret['detail']=res_list
    else:
        ret['code']=r.status_code
    return ret


params=getTracks(middle_start=100, middle_end=102, start=1, end=6)
