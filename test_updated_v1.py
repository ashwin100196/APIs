# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 14:37:57 2017

@author: TR100083 | Ashwin
"""

"""
###################################################################
MAIN FILE
###################################################################
"""

import web
import time
import datetime

# Create your views here.

import json
from pymongo import MongoClient
client = MongoClient('mongodb://heroku_z9l8tf4w:g3l5j5hbh755td1sm8e0pf30er@ds117605.mlab.com:17605/heroku_z9l8tf4w')
db = client.get_database()
alerts = db.alarm_history


urls = (
    '/home', 'get_home',
    '/alertboxes', 'get_contact_blocks',
    '/timeline','get_timeline'
)
app = web.application(urls, globals())

def time_stamp(t):
    timestamp = time.mktime(time.strptime(t,'%Y/%m/%d %H:%M:%S'))
    return timestamp

def sum_the_count(cursor):
    flag = 1
    total = 0.0
    prev = 0
    curval = 0
    alert_count = cursor.count()
    if not alert_count : 
        return total, curval
    for alarm in cursor:
        if flag : 
            curval = alarm['count']
            flag = 0
        if alarm['count']>prev:
            total += alarm['count']-prev
        prev = alarm['count']
    return (total/alert_count, curval)

class get_home:    
    def get_table(self,index):
        #initialize maximum and minimum values
        arr_hlth_min = [0.0,2.0,5.0,4.0,0.0]
        arr_hlth_max = [10.0,15.0,13.0,8.0,1.0]
        events = ["Human detected","hardhat","safetyglasses","hearingprotection","spill"]
        cursor = alerts.find({"$and":[{"type":events[index]},{"timestamp":{"$gt":self.time_start,"$lt":self.time_end}}]}).sort([("timestamp" , -1)])
        avg,curval = sum_the_count(cursor)
        rating = 1 + int((arr_hlth_max[index]-curval)/(arr_hlth_max[index]-arr_hlth_min[index])*5)
        if rating >5: rating =5
        if rating<0 : rating = 0
        if rating<=2:
            risk = "High"
        elif rating ==3:
            risk = "Moderate"
        else :
            risk = "Low"

        response = {"Event name":events[index],"Health zone min": arr_hlth_min[index], "Health zone max": arr_hlth_max[index],
        "Current value":curval,"Average":avg, "Rating":rating, "Risk" : risk}
        return response

    def GET(self):  
        client_input = web.input()

        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        t_start = client_input.t_start
        t_end = client_input.t_end

        self.time_start = time_stamp(t_start)
        self.time_end = time_stamp(t_end)
        

        #print(query)
        #print(location_id)
        #print(cctv_id)
        #print(event_type)
        #print(time_start)
        #print(time_end)
        resp1 = self.get_table(0)
        resp2 = self.get_table(1)
        resp3 = self.get_table(2)
        resp4 = self.get_table(3)
        resp5 = self.get_table(4)
        
        resp_data = [resp1,resp2,resp3,resp4,resp5]
        return json.dumps(resp_data)


class get_contact_blocks:
    def GET(self):
        client_input = web.input()

        query = client_input.query
        if query =='start':
            icon_str1 = ''
            icon_str2 = ''
            icon_str3 = ''
            cursor = alerts.find({"$and":[{"alert":True},{"type":"Human detected"}]} ).sort([("timestamp" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str1 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":True},{"type":"hardhat"}]} ).sort([("timestamp" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str2 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":True},{"type":"safetyglasses"}]} ).sort([("timestamp" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str3 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            resp_data = [{"Block":'Human detected',"Block icon":icon_str1},
            {"Block":'Hardhat not worn',"Block icon":icon_str2},
            {"Block":'Safety glasses not worn',"Block icon":icon_str3},
            {"Block":'Spill detected',"Block icon":''},
            {"Block":'Hearing protection not worn',"Block icon":''}]
            return json.dumps(resp_data)
        else :
            return "Error"


class get_timeline:
    def GET(self):
        # client_input = web.input()
        # location_id = client_input.l_id
        # cctv_id = client_input.cc_id
        # t_start = client_input.t_start
        # t_end = client_input.t_end

        # time_start = time_stamp(t_start)
        # time_end = time_stamp(t_end)

        # cursor = alerts.find({"$and":[{"timestamp":{"$gt":time_start,"$lt":time_end}}]},{'_id': False}).sort([("timestamp" , 1)])
        # j = []
        # for alert in cursor:
        #     #print(alert)
        #     alert['timestamp'] = datetime.datetime.fromtimestamp(int(alert['timestamp']+19800)).strftime('%d-%m-%Y %H:%M:%S')
        #     j.append(alert)
        # return json.dumps(j)
        web.header('Content-Type', 'text/json')
        web.header('Access-Control-Allow-Origin','*')
        timeline = [
            { "caption": '16 Jan', "date": datetime.date(2014, 1, 16).isoformat(), "selected": True, "title": 'Human detected', "content": '0' },
            { "caption": '28 Feb', "date": datetime.date(2014, 2, 28).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '20 Mar', "date": datetime.date(2014, 3, 20).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '20 May', "date": datetime.date(2014, 5, 20).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '09 Jul', "date": datetime.date(2014, 7, 9).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '30 Aug', "date": datetime.date(2014, 8, 30).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '15 Sep', "date": datetime.date(2014, 9, 15).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '01 Nov', "date": datetime.date(2014, 11, 1).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '10 Dec', "date": datetime.date(2014, 12, 10).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '29 Jan', "date": datetime.date(2015, 1, 19).isoformat(), "title": 'Hard hat', "content": '0' },
            { "caption": '3 Mar', "date": datetime.date(2015, 3, 3).isoformat(), "title": 'Hard hat', "content": '0' },
        ]

        return json.dumps(timeline)


print("Server Started at:")

if __name__ == "__main__":

    app.run()
