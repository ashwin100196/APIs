# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:37:57 2017

@author: IN0120 | Sanat Dutta
"""

"""
###################################################################
MAIN FILE
###################################################################
"""

import web
import time

# Create your views here.

import json
from pymongo import MongoClient
client = MongoClient('mongodb://heroku_z9l8tf4w:g3l5j5hbh755td1sm8e0pf30er@ds117605.mlab.com:17605/heroku_z9l8tf4w')
db = client.get_database()
alerts = db.alarm_history


urls = (
    '/alerthistory', 'alert_history',
    '/falsealerts','false_alert',
    '/alerts', 'get_mainpage',
    '/alertboxes', 'get_contact_blocks',
    '/filterloc', 'populate_location',
    '/filtercc', 'populate_cctv',
    '/filtertype', 'populate_type',
)
app = web.application(urls, globals())

def sum_the_time(cursor,time_start,time_end):
    temp_time = time_start
    sum=0.0
    for alarm in cursor:
        if alarm['condition']:
            temp_time = alarm['timestamp']
        else:
            sum += alarm['timestamp']-temp_time
            temp_time = alarm['timestamp']
    return sum

class alert_history:    
    def GET(self):  
        client_input = web.input()

        query = client_input.query
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        time_start = int(client_input.t_start)
        time_end = int(client_input.t_end)

        print(query)
        print(location_id)
        print(cctv_id)
        print(event_type)
        print(time_start)
        print(time_end)

        if query == 'alert-history':
            if event_type == 'all':
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c1 = cursor.count()
                sum1 = sum_the_time(cursor,time_start,time_end)
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c2 = cursor.count()
                sum2 = sum_the_time(cursor,time_start,time_end)
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c3 = cursor.count()
                sum3 = sum_the_time(cursor,time_start,time_end)
                t_sum = sum1+sum2+sum3
                alert_piechart_p1 = sum1/t_sum*100.0
                alert_piechart_p2 = sum2/t_sum*100.0
                alert_piechart_p3 = sum3/t_sum*100.0
                remaining_pie = 100.0-alert_piechart_p1-alert_piechart_p2-alert_piechart_p3
                true_alerts = c1+c2+c3
                total_alerts = alerts.find({"timestamp":{"$gt":time_start,"$lt":time_end}}).count()
                false_percentage = (1-(true_alerts/total_alerts))*100.0
                resp_data = {"Percentage1":alert_piechart_p1,"Percentage2":alert_piechart_p2,"Percentage3":alert_piechart_p3,"Percentage4":remaining_pie}
                return json.dumps(resp_data)
            else:
                print('hi')
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                print(cursor.count())
                true_alerts = cursor.count()
                sum = sum_the_time(cursor,time_start,time_end)
                piechart_percentage = sum/86400*100.0
                remaining_pie = 100-piechart_percentage
                total_alerts = alerts.find({"$and":[{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]}).count()
                false_percentage = (1-(true_alerts/total_alerts))*100
                resp_data = {"Percentage1":piechart_percentage,"Percentage2":remaining_pie}
                return json.dumps(resp_data)
        else:
            return "Error"

class false_alert:    
    def GET(self):  
        client_input = web.input()

        query = client_input.query
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        time_start = int(client_input.t_start)
        time_end = int(client_input.t_end)

        if query == 'false-alert':
            if event_type == 'all':
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c1 = cursor.count()
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c2 = cursor.count()
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                c3 = cursor.count()
                true_alerts = c1+c2+c3
                total_alerts = alerts.find({"timestamp":{"$gt":time_start,"$lt":time_end}}).count()
                true_percentage = true_alerts/total_alerts*100.0
                false_percentage = 100-true_percentage
                resp_data = {"False alert percentage" : false_percentage,"True alert percentage" : true_percentage}
                return json.dumps(resp_data)
            else:
                cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
                true_alerts = cursor.count()
                total_alerts = alerts.find({"$and":[{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]}).count()
                true_percentage = true_alerts/total_alerts*100.0
                false_percentage = 100-true_percentage
                resp_data = {"False alert percentage" : false_percentage,"True alert percentage" : true_percentage}
                return json.dumps(resp_data)
        else:
            return "Error"

class get_mainpage:    
    def GET(self):      
        new_time = time.time()
        old_time = new_time - 86400.0
        print(new_time)
        print(old_time)
        client_input = web.input()

        query = client_input.query
        if query =='start':
            cursor = alerts.find({"$and":[{"alert":"True"},{"timestamp":{"$gt":old_time,"$lt":new_time}}]})
            sum_time = sum_the_time(cursor,old_time,new_time)
            Mainchart_gage = sum_time/86400.0*100
            resp_data = {"Gage value":Mainchart_gage}
            return json.dumps(resp_data)
        else:
            return "Error"

class get_contact_blocks:
    def GET(self):
        client_input = web.input()

        query = client_input.query
        if query =='start':
            icon_str1 = ''
            icon_str2 = ''
            icon_str3 = ''
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str1 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":"True"},{"type":"hardhat"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str2 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":"True"},{"type":"safetyglasses"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str3 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            resp_data = {"Block string1":'Human detected',"Block icon string1":icon_str1,
            "Block string2":'hardhat not worn',"Block icon string2":icon_str2,
            "Block string3":'safety glasses not worn',"Block icon string3":icon_str3}
            return json.dumps(resp_data)
        else :
            return "Error"

class populate_location:
    def GET(self):
        resp_data = {"Location":[1,2,3]}
        return json.dumps(resp_data)

class populate_cctv:
    def GET(self):
        resp_data = {"CCTV":[1,2,3]}
        return json.dumps(resp_data)

class populate_type:
    def GET(self):
        resp_data = {"Event type":'human detected'}
        return json.dumps(resp_data)
#,'hardhat not worn','safety glasses not worn']


print("Server Started at:")

if __name__ == "__main__":

    app.run()