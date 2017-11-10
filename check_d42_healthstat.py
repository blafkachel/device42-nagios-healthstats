#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import requests
requests.packages.urllib3.disable_warnings()
import base64
import json
import argparse

class REPORT():
    def __init__(self):
        pass

    def output(self, msg):
        #if LOGFILE and LOGFILE != '':
        #    with codecs.open(self.logfile, 'a', encoding = 'utf-8') as f:
        #        f.write(msg.strip()+'\r\n')  # \r\n for notepad
        if debug == 'True':
            try:
                print msg
            except:
                print msg.encode('ascii', 'ignore') + ' # < non-ASCII chars detected! >'


class REST():
    def __init__(self):
        self.base_url = D42_HOST

    def fetcher(self, url):
        #headers = {
        #    'Authorization': 'Basic ',
        #    'Content-Type': 'application/x-www-form-urlencoded'
        #}

        #r = requests.get(url, headers=headers, verify=False)
        if debug == True: print url
        r = requests.get(url, verify=False)
        msg = 'Status code: %s' % str(r.status_code)
        logger.output(msg)
        msg = str(r.text)
        logger.output(msg)
        return r.text

    def get_data(self):
        url = d_http+'://'+self.base_url+':'+d_port+'/healthstats/'
        msg =  '\r\nFetching healthstats from %s ' % url
        logger.output(msg)
        data = self.fetcher(url)
        return data

class PROCESS():
    def tresholds(self,current,warn,crit):
        #https://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT
        if current < warn: data='OK'
        if current > warn and current < crit: data='WARNING'
        if current > crit: data='CRITICAL'

        if warn.strip()[-1]==':' or crit.strip()[-1]==':':
            warn = int(warn.replace(':',''))
            crit = int(crit.replace(':',''))
            if current > warn: data='OK'
            if current < warn and current > crit: data='WARNING'
            if current < crit: data='CRITICAL'

        return data

    def convert(self,metric,value):
        #https://nagios-plugins.org/doc/guidelines.html#AEN200
        if 'percent' in metric:
            data = str(float(value))+'%'

        #convert values to MB
        elif 'kb' in value.lower(): data = str(float(value.split()[0])/1024)+'MB' # KB to MB
        elif 'mb' in value.lower(): data = str(float(value.split()[0]))+'MB' # MB to MB
        elif 'gb' in value.lower(): data = str(float(value.split()[0])*1024)+'MB' # GB to MB
        elif 'buffer' in metric: data = value
        else: data = value+'MB'

        return data

def main():
    global result,d_warn,d_crit,memitem
    minmax = ';0;0'
    raw = rest.get_data()
    data = json.loads(raw)

    #cpu_pct = data['cpu_used_percent']
    for i in data:
        if i.lower() == d_metric.lower():
            if i.lower() == 'backup_status':
                msg = ''
                status = 'OK'
                backups = data['backup_status']
                if len(backups) == 0:
                    status = 'WARNING'
                    msg = ' - No backupjobs defined'
                for backup in backups:
                    #print backup['status']
                    #print backup['id']
                    #print backup['job_name']
                    if 'please check' in backup['status'].lower():
                        if not status == 'CRITICAL': status = 'WARNING'
                        if not backup['job_name'] in msg: msg = msg + 'job:' + backup['job_name']+' status:'+backup['status']+'\n'

                    if 'not run' in backup['status'].lower():
                        status = 'CRITICAL'
                        if not backup['job_name'] in msg: msg = msg + 'job:' + backup['job_name']+' status:'+backup['status']+'\n'

                    if 'good' in backup['status'].lower():
                        status = 'OK'
                        if not backup['job_name'] in msg: msg = msg + 'job:' + backup['job_name']+' status:'+backup['status'].replace('\n','')+'\n'

                # Print results
                print status+': '+i+' '+msg
                result = status
            elif i.lower() == 'memory_in_mb':
                mems = data['memory_in_MB']

                #print mems
                for mem in mems:
                    if mem.lower() == memitem.lower().replace('percent',''):
                        value = process.convert(mem,str(mems[mem]))
                        status = process.tresholds(mems[mem],d_warn,d_crit)

                        if memitem.lower() == 'memfreepercent':
                            memtotal = float(mems['memtotal'])
                            memfree = float(mems['memfree'])
                            value = process.convert(memitem,(memfree/memtotal*100))
                            status = process.tresholds(value,d_warn,d_crit)

                        if memitem.lower() == 'swapfreepercent':
                            memtotal = float(mems['swaptotal'])
                            memfree = float(mems['swapfree'])
                            value = process.convert(memitem,(memfree/memtotal*100))
                            status = process.tresholds(value,d_warn,d_crit)

                # Print results
                if 'percent' in i.lower() or 'percent' in memitem:
                    minmax=''
                print status+': '+memitem+' '+value+'|'+memitem+'='+value+';'+d_warn+';'+d_crit+minmax
                result = status
            else:
                #Check on tresholds
                value = process.convert(i.lower(),data[i])
                status = process.tresholds(data[i],d_warn,d_crit)

                # Print results
                if 'percent' in i.lower():
                    minmax=''
                print status+': '+i+' '+value+'|'+i+'='+value+';'+d_warn+';'+d_crit+minmax

                result = status
    return

if __name__ == '__main__':
    global result,memitem
    #usagemessage  =   'Usage: check_d42_healthstat.py {-h for more detailed info}'
    #if len(sys.argv) < 2 :
    #  print usagemessage
    #  sys.exit()
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='debug option, show output on the console')
    parser.add_argument('-i', help='host instance to check')
    parser.add_argument('-m', help='metric name')
    parser.add_argument('-p', help='port (default is 4343)')
    parser.add_argument('-s', help='set non-ssl options:http/https (default is https)')
    parser.add_argument('-w', help='set warning treshold')
    parser.add_argument('-c', help='set critical treshold')


    args = parser.parse_args()
    debug = False
    d_metric = ''
    if args.d:
        debug = True
    if args.i:
        D42_HOST = args.i
    else:
        from params import D42_HOST
    if args.p:
        d_port = args.p
    else:
        d_port = '4343'
    if args.s:
        d_http = args.s
    else:
        d_http = 'https'
    if args.m:
        d_metric = args.m
        #cpu_used_percent
        #dbsize
        #disk_used_percent
        #memtotal
        #cached
        #swapfree
        #swaptotal
        #memfree
        #buffers
    if args.w:
        d_warn = args.w
    if args.c:
        d_crit = args.c

    if debug == True : print args

    memoryobjects = ['memtotal','memfree','memfreepercent','cached','swaptotal','swapfree','swapfreepercent','buffers']
    if d_metric in memoryobjects:
        memitem = d_metric
        d_metric = 'memory_in_mb'
    if not d_metric.lower() =='backup_status' and not (args.w or args.c):
        print 'UNKNOWN: '+d_metric+' - no warning or critical tresholds provided'
        sys.exit(3)

    logger = REPORT()
    rest = REST()
    process = PROCESS()
    main()

    if 'ok' in result.lower():
         sys.exit(0)
    if 'warning' in result.lower():
         sys.exit(1)
    if 'critical' in result.lower():
         sys.exit(2)
    if 'unknown' in result.lower():
         sys.exit(3)
    sys.exit()
