#!/usr/bin/env python
#encoding: utf8

#refer http://tkf.github.io/2011/04/20/visualizing-git-and-hg-commit-activity.html

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from collections import Counter
from datetime import datetime
import time
import numpy
from matplotlib import pyplot
from matplotlib.dates import YearLocator, MonthLocator, DayLocator, WeekdayLocator, DateFormatter, MO
from matplotlib.ticker import NullFormatter
from matplotlib.dates import epoch2num, date2num

def outputCnt(cnt):
    for ele in cnt.most_common():
        print '%s, %s' %(ele[0], ele[1])
    print ''

def statusComp(query):
    #time_AS, time_DS, time_AD, time_AC, time_DC, time_DD, time_DL
    patterns=['已到达始发站','已离开始发站','已到达目的站','进入清关流程','放行','配送中心','已签收'] #'补充资料','成功上传'
    for i,pattern in enumerate(patterns):
        if query.find(pattern)>-1:
            return i
    return len(patterns)

def tsParse(query):
    return int(time.mktime(datetime.strptime(query, '%Y/%m/%d %H:%M:%S').timetuple()))


def read_dates(input):
    dates = []
    for line in input:
        num = epoch2num(float(line))
        dates.append(num)
    return dates


def plot_datehist(dates, bins, relativeFlag=False, title=None, xlabel=None, ylabel=None, xmax=None):
    (hist, bin_edges) = numpy.histogram(dates, bins)
    width = bin_edges[1] - bin_edges[0]
 
    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    ax.bar(bin_edges[:-1], hist / width, width=width)
    if xmax==None:
        ax.set_xlim(bin_edges[0], max(dates))#num_now())
    else:
        ax.set_xlim(bin_edges[0], xmax)#num_now())
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    # set x-ticks in date
    # see: http://matplotlib.sourceforge.net/examples/api/date_demo.html
    
    if not relativeFlag:
        # ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.xaxis.set_minor_locator(WeekdayLocator(byweekday=MO, interval=2))
        # ax.xaxis.set_minor_locator(DayLocator(bymonthday=[1,16]))
        ax.xaxis.set_minor_formatter(DateFormatter('%b.%d'))
        # ax.xaxis.set_minor_locator(DayLocator(bymonthday=[1,16]))
        # ax.xaxis.set_minor_formatter(DateFormatter('%d'))
    
    else:
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.xaxis.set_minor_locator(DayLocator())
        ax.xaxis.set_minor_formatter(DateFormatter('%d'))
    # format the coords message box
    ax.format_xdata = DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()
    ax.grid(True)
    return fig


with open('tracks.json') as file:
    lineCount=0
    bases=[]
    codes=[]
    middles=[]
    details=[]
    statuses=[]
    locations=[]
    
    time_AS=[]
    time_DS=[]
    time_AD=[]
    time_AC=[]
    time_DC=[]
    time_DD=[]
    time_DL=[]
    time_AS_DS=[]
    time_DS_AD=[]
    time_AD_AC=[]
    time_AC_DC=[]
    time_DC_DD=[]
    time_DD_DL=[]
    for line in file:
        lineCount+=1
        # if lineCount <56438:
        #     continue
        # if lineCount>=186440:
        #     break
        
        record=json.loads(line.strip())
        bases.append(record['base'])
        codes.append(record['code'])
        middles.append(record['middle'])

        if record['code']==200:
            
            statusSet=set()
            locationSet=set()
            status_time=[None]*8
            
            for detail in record['detail']:
                if detail['status'] not in statusSet:
                    statusSet.add(detail['status'])
                if detail['location'] not in locationSet:
                    locationSet.add(detail['location'])
                
                status_index=statusComp(detail['status'])
                if detail['time'].startswith('1900'):
                    continue
                if status_time[status_index]==None:
                    status_time[status_index]=tsParse(detail['time'])
                elif status_time[status_index]>tsParse(detail['time']):
                    status_time[status_index]=tsParse(detail['time'])

            if status_time[0]!=None:
                time_AS.append(status_time[0])
            if status_time[1]!=None:
                time_DS.append(status_time[1])
            if status_time[2]!=None:
                time_AD.append(status_time[2])
            if status_time[3]!=None:
                time_AC.append(status_time[3])
            if status_time[4]!=None:
                time_DC.append(status_time[4])
            if status_time[5]!=None:
                time_DD.append(status_time[5])
            if status_time[6]!=None:
                time_DL.append(status_time[6])
            
            
            if status_time[0]!=None and status_time[1]!=None:
                if status_time[1]-status_time[0]>0:
                    time_AS_DS.append(status_time[1]-status_time[0])#+1420041600)
            if status_time[1]!=None and status_time[2]!=None:
                if status_time[2]-status_time[1]>0:
                    time_DS_AD.append(status_time[2]-status_time[1])#+1420041600)
            if status_time[3]!=None and status_time[4]!=None:
                if status_time[4]-status_time[3]>0:
                    time_AC_DC.append(status_time[4]-status_time[3])#+1420041600)
            if status_time[4]!=None and status_time[5]!=None:
                if status_time[5]-status_time[4]>0:
                    time_DC_DD.append(status_time[5]-status_time[4])#+1420041600)
            if status_time[5]!=None and status_time[6]!=None:
                if status_time[6]-status_time[5]>0:
                    time_DD_DL.append(status_time[6]-status_time[5])#+1420041600)

            
            statuses.extend(list(statusSet))
            locations.extend(list(locationSet))
            details.append(len(statusSet))
    
    baseCnt=Counter(bases)
    codeCnt=Counter(codes)
    middleCnt=Counter(middles)
    detailCnt=Counter(details)
    statusCnt=Counter(statuses)
    locationCnt=Counter(locations)   


    fig = plot_datehist(read_dates(time_AS), 90, relativeFlag=False, title='到达美国仓库的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')
    fig = plot_datehist(read_dates(time_DS), 90, relativeFlag=False, title='离开美国仓库的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')
    fig = plot_datehist(read_dates(time_AD), 90, relativeFlag=False, title='到达中国仓库的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')
    fig = plot_datehist(read_dates(time_AC), 90, relativeFlag=False, title='进入清关流程的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')
    #fig = plot_datehist(read_dates(time_DC), 40, relativeFlag=False, title='清关结束 直方图', xlabel='日期', ylabel='订单数')
    fig = plot_datehist(read_dates(time_DD), 90, relativeFlag=False, title='开始国内配送的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')
    fig = plot_datehist(read_dates(time_DL), 90, relativeFlag=False, title='已经签收的订单 统计图', xlabel='日期（2014.10-2015.5）', ylabel='订单数')

    fig = plot_datehist(read_dates(time_AS_DS), 30, relativeFlag=True, title='美国仓库耗时 统计直方图', xlabel='耗时(单位：天)', ylabel='订单数', xmax=epoch2num(float(3600*24*20)))
    fig = plot_datehist(read_dates(time_DS_AD), 30, relativeFlag=True, title='国际运输耗时 统计直方图', xlabel='耗时(单位：天)', ylabel='订单数', xmax=epoch2num(float(3600*24*20)))
    fig = plot_datehist(read_dates(time_AC_DC), 30, relativeFlag=True, title='清关耗时 统计直方图', xlabel='耗时(单位：天)', ylabel='订单数', xmax=epoch2num(float(3600*24*20)))
    #fig = plot_datehist(read_dates(time_DC_DD), 30, relativeFlag=True, title='国内配送耗时1 直方图', xlabel='耗时', ylabel='订单数')#, xmax=epoch2num(float(3600*24*20)))
    fig = plot_datehist(read_dates(time_DD_DL), 30, relativeFlag=True, title='国内配送耗时 统计直方图', xlabel='耗时(单位：天)', ylabel='订单数', xmax=epoch2num(float(3600*24*20)))

    pyplot.show()
    
    # print 'done reading %d lines' %lineCount
    #outputCnt(baseCnt)
    #outputCnt(codeCnt)
    #outputCnt(middleCnt)
    
    outputCnt(detailCnt)
    outputCnt(statusCnt)
    outputCnt(locationCnt)
    

        