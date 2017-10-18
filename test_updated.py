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
    '/recentalerts','recent_alerts'
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

        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        time_start = int(client_input.t_start)
        time_end = int(client_input.t_end)

        #print(query)
        #print(location_id)
        #print(cctv_id)
        #print(event_type)
        #print(time_start)
        #print(time_end)
        if event_type == 'all':
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum1 = sum_the_time(cursor,time_start,time_end)
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum2 = sum_the_time(cursor,time_start,time_end)
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum3 = sum_the_time(cursor,time_start,time_end)
            t_sum = sum1+sum2+sum3
            alert_piechart_p1 = sum1/t_sum*100.0
            alert_piechart_p2 = sum2/t_sum*100.0
            alert_piechart_p3 = sum3/t_sum*100.0
            remaining_pie = 100.0-alert_piechart_p1-alert_piechart_p2-alert_piechart_p3
            resp_data = [{"Percentage":alert_piechart_p1},{"Percentage":alert_piechart_p2},{"Percentage":alert_piechart_p3},{"Percentage":remaining_pie}]
            return json.dumps(resp_data)
        else:
            #print('hi')
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            #print(cursor.count())
            sum = sum_the_time(cursor,time_start,time_end)
            piechart_percentage = sum/86400*100.0
            remaining_pie = 100-piechart_percentage
            resp_data = [{"Percentage":piechart_percentage},{"Percentage":remaining_pie}]
            return json.dumps(resp_data)

class false_alert:    
    def GET(self):  
        client_input = web.input()
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        time_start = int(client_input.t_start)
        time_end = int(client_input.t_end)

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
            resp_data = [{"Percentage" : false_percentage},{"Percentage" : true_percentage}]
            return json.dumps(resp_data)
        else:
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            true_alerts = cursor.count()
            total_alerts = alerts.find({"$and":[{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]}).count()
            true_percentage = true_alerts/total_alerts*100.0
            false_percentage = 100-true_percentage
            resp_data = [{"Percentage" : false_percentage},{"Percentage" : true_percentage}]
            return json.dumps(resp_data)

class get_mainpage:    
    def GET(self):      
        new_time = time.time()
        old_time = new_time - 86400.0
        print(new_time)
        print(old_time)
        client_input = web.input()

        query = client_input.query
        if query =='start':
            cursor = alerts.find({"$and":[{"alert":'True'},{"timestamp":{"$gt":old_time,"$lt":new_time}}]})
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
            resp_data = [{"Block":'Human detected',"Block icon":icon_str1},
            {"Block":'hardhat not worn',"Block icon":icon_str2},
            {"Block":'safety glasses not worn',"Block icon":icon_str3}]
            return json.dumps(resp_data)
        else :
            return "Error"

class populate_location:
    def GET(self):
        resp_data = [{"Location":'1'},{"Location":'2'},{"Location":'3'}]
        return json.dumps(resp_data)

class populate_cctv:
    def GET(self):
        resp_data = [{"CCTV":'1'},{"CCTV":'2'},{"CCTV":'3'}]
        return json.dumps(resp_data)

class populate_type:
    def GET(self):
        resp_data = [{"Event type":'all'},{"Event type":'human detected'},{"Event type":'hard hat not worn'},{"Event type":'safety glasses missing'}]
        return json.dumps(resp_data)

class recent_alerts:
    def GET(self):
        client_input = web.input()
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        time_start = int(client_input.t_start)
        time_end = int(client_input.t_end)

        if event_type == 'all':
            cursor = alerts.find({"$and":[{"alert":"True"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]},{'_id': False})
            j=[]
            for alert in cursor:
                #print(alert)
                j.append(alert)
            return json.dumps(j)
        else:
            cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]},{'_id': False})
            j=[]
            for alert in cursor:
                #print(alert)
                j.append(alert)
            return json.dumps(j)


print("Server Started at:")

if __name__ == "__main__":

    app.run()