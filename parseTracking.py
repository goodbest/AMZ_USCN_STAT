import requests
from bs4 import BeautifulSoup as bs




def generateParams(prefix, middle_start=120, middle_end=135, start=1, end=2):
    
    trackNumbers=[]    
    for middle in range(middle_start, middle_end):
        for i in range(start, end):
            trackNumber='%s%03d%07d' %(prefix, middle, i)
            trackNumbers.append(trackNumber)
    
    params=[]
    for trackNumber in trackNumbers:
        param={}
        param['lang']='zh'
        param['trackingno']=trackNumber
        params.append(param)
    
    return params


def getTrackInfo(param):
    r = requests.get("https://www.ecmsglobal.com/oms/showtracking", params=param)
    if r.status_code==200:
        text= bs(r.text)
        dls=text.findAll("dl", class_="trackList")
        if len(dls)>0:
            dds=dls[0].findAll("dd")
            if len(dds)>0:
                for dd in dds:
                    divn=dd.findAll("div", class_="n")
                    if len(divn)>0:
                        trackStatus=divn[0].contents[0]
                        print trackStatus
                    divw=dd.findAll("div", class_="w")
                    if len(divw)>0:
                        if len(divw[0].contents)>0:
                            trackLoca=divw[0].contents[0]
                        else:
                            trackLoca=''
                        print trackLoca
                    divt=dd.findAll("div", class_="t")
                    if len(divt)>0:
                        trackTime=divt[0].contents[0]
                        print trackTime




params=generateParams('APELAX', middle_start=122, middle_end=124, start=1, end=5)
getTrackInfo(params[0])