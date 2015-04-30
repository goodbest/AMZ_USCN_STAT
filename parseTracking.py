import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from bs4 import BeautifulSoup as bs
import time
from pymongo import MongoClient
import dbConfig as dbc
import argparse

middles={}
middles['APELAX']= [104, 110, 111, 115, 116, 118, 119, 122, 131, 132, 133]
middles['APECHI']= [100, 101, 102, 103, 105, 106, 107, 108, 109, 112, 113, 114, 117, 120, 121, 123, 124, 125, 126, 127, 128, 129, 130, 134]
#db, collection
mdb=dbc.init_db('tracks','tracks')

def getTracks(middle_start, middle_end, start, end, countThres=50, chunkSize=30, timesleep=1):
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
            print trackNumber
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
        if len(chunks)>0:
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
                        if len(divn[0].contents)>0:
                            trackStatus=divn[0].contents[0]
                        else:
                            trackStatus=''
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
                        if len(divt[0].contents)>0:
                            trackTime=divt[0].contents[0]
                        else:
                            trackTime=''
                        res['time']=trackTime
                    else:
                        continue
                    res_list.append(res)
        ret['code']=200
        ret['detail']=res_list
    else:
        ret['code']=r.status_code
    return ret

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="query amazon tracks")
    parser.add_argument('-ms', '--middle-start',
                        dest    = 'middle_start',
                        default = '100',
                        nargs   = '?',
                        type    = int,
                        help    = "middle start value")
    parser.add_argument('-me', '--middle-end',
                        dest    = 'middle_end',
                        default = '134',
                        nargs   = '?',
                        type    = int,
                        help    = "middle end value")
    parser.add_argument('-s', '--start',
                        dest    = 'start',
                        default = '1',
                        nargs   = '?',
                        type    = int,
                        help    = "start value")
    parser.add_argument('-e', '--end',
                        dest    = 'end',
                        default = '10000000',
                        nargs   = '?',
                        type    = int,
                        help    = "end value")
    parser.add_argument('-ts', '--time-sleep',
                        dest    = 'time_sleep',
                        default = '1',
                        nargs   = '?',
                        type    = int,
                        help    = "sleep time")
    args = parser.parse_args()
    
    # sys.stdout = open('ms%s_me%s_s%s_e%s.log' %(args.middle_start, args.middle_end, args.start, args.end), 'w', 0)
    params=getTracks(middle_start=args.middle_start, middle_end=args.middle_end, start=args.start, end=args.end)
