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
#imports
import web
import date
import time
import datetime



import json
from pymongo import MongoClient
#connect to mongo db
client = MongoClient('mongodb://heroku_z9l8tf4w:g3l5j5hbh755td1sm8e0pf30er@ds117605.mlab.com:17605/heroku_z9l8tf4w')
db = client.get_database()
alerts = db.alarm_history

#set url paths
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

#converting time to unix
def time_stamp(t):
    timestamp = time.mktime(time.strptime(t,'%Y/%m/%d %H:%M:%S'))
    return timestamp

#to calculate total duration of time when alarm was on.
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

#class to deliver alert history
class alert_history:    
    def GET(self):  
        #inputs
        client_input = web.input()

        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        t_start = client_input.t_start
        t_end = client_input.t_end

        time_start = time_stamp(t_start)
        time_end = time_stamp(t_end)

        #print(query)
        #print(location_id)
        #print(cctv_id)
        #print(event_type)
        #print(time_start)
        #print(time_end)

        #obtain alert history for each event from db
        #for all events
        if event_type == 'all':
            cursor = alerts.find({"$and":[{"alert":True},{"type":"Human detected"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum1 = sum_the_time(cursor,time_start,time_end)
            cursor = alerts.find({"$and":[{"alert":True},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum2 = sum_the_time(cursor,time_start,time_end)
            cursor = alerts.find({"$and":[{"alert":True},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            sum3 = sum_the_time(cursor,time_start,time_end)
            t_sum = time_end-time_start
            #convert to percentage values
            try:
                alert_piechart_p1 = sum1/t_sum*100.0
                alert_piechart_p2 = sum2/t_sum*100.0
                alert_piechart_p3 = sum3/t_sum*100.0
            except:
                alert_piechart_p1 = sum1/1*100.0
                alert_piechart_p2 = sum2/1*100.0
                alert_piechart_p3 = sum3/1*100.0
            remaining_pie = 100.0-alert_piechart_p1-alert_piechart_p2-alert_piechart_p3
            resp_data = [{"Event Name":"Human detected","Percentage":alert_piechart_p1},{"Event Name":"Hard hat not worn","Percentage":alert_piechart_p2},
            {"Event Name":"Safety glasses not worn","Percentage":alert_piechart_p3},{"Event Name":'Closed toed shoes not worn',"Percentage":0.0},
            {"Event Name":'Gloves not worn',"Percentage":0.0},{"Event Name":'Spill detected',"Percentage":0.0},{"Event Name":'Coupling breakage detected',"Percentage":0.0},
            {"Event Name":'Hearing protection not worn',"Percentage":0.0},{"Event Name":"No alerts","Percentage":remaining_pie}]
            return json.dumps(resp_data)
        else:
        #for a single event
            #print('hi')
            cursor = alerts.find({"$and":[{"alert":True},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            #print(cursor.count())
            sum = sum_the_time(cursor,time_start,time_end)
            piechart_percentage = sum/(time_end-time_start)*100.0
            remaining_pie = 100-piechart_percentage
            resp_data = [{"Event Name":event_type,"Percentage":piechart_percentage},{"Event Name":"No alerts","Percentage":remaining_pie}]
            return json.dumps(resp_data)

#false alert updating -- ignore this block
class false_alert:    
    def GET(self):  
        client_input = web.input()
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        t_start = client_input.t_start
        t_end = client_input.t_end

        time_start = time_stamp(t_start)
        time_end = time_stamp(t_end)
        print(time_start,time_end)

        if event_type == 'all':
            cursor = alerts.find({"$and":[{"alert":True},{"type":"Human detected"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            c1 = cursor.count()
            cursor = alerts.find({"$and":[{"alert":True},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            c2 = cursor.count()
            cursor = alerts.find({"$and":[{"alert":True},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            c3 = cursor.count()
            true_alerts = c1+c2+c3
            total_alerts = alerts.find({"timestamp":{"$gt":time_start,"$lt":time_end}}).count()
            try:
                true_percentage = true_alerts/total_alerts*100.0
                false_percentage = 100-true_percentage
            except:
                resp_data = [{"Percentage" : 100.0}]
                return json.dumps(resp_data)
            resp_data = [{"Event Name":"True","Percentage" : true_percentage},{"Event Name":"False","Percentage" : false_percentage}]
            return json.dumps(resp_data)
        else:
            cursor = alerts.find({"$and":[{"alert":True},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
            true_alerts = cursor.count()
            total_alerts = alerts.find({"$and":[{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]}).count()
            try:
                true_percentage = true_alerts/total_alerts*100.0
                false_percentage = 100-true_percentage
            except:
                resp_data = [{"Percentage" : 100.0}]
                return json.dumps(resp_data)
            resp_data = [{"Event Name":"True","Percentage" : true_percentage},{"Event Name":"False","Percentage" : false_percentage}]
            return json.dumps(resp_data)

#obtains the overall risk as a gage valure
class get_mainpage:    
    def GET(self):      
        new_time = time.time()
        old_time = new_time - 86400.0
        print(new_time)
        print(old_time)
        client_input = web.input()

        query = client_input.query
        if query =='start':
            cursor = alerts.find({"$and":[{"alert":True},{"timestamp":{"$gt":old_time,"$lt":new_time}}]})
            sum_time = sum_the_time(cursor,old_time,new_time)
            if sum_time<1800:
                Mainchart_gage = sum_time/1800.0*20
            elif sum_time>=1800 and sum_time<7200:
                Mainchart_gage = 20.0+(sum_time-1800)/5400.0*30
            else :
                Mainchart_gage = 50.0+(sum_time-7200)/79200.0*50
            resp_data = [{"Gage value":Mainchart_gage}]
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
            cursor = alerts.find({"$and":[{"alert":True},{"type":"Human detected"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str1 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":True},{"type":"hardhat"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str2 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            cursor = alerts.find( {"$and":[{"alert":True},{"type":"safetyglasses"}]} ).sort([("$natural" , -1)]).limit(1);
            for alarm in cursor:
                if alarm['condition']:
                    icon_str3 = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i>'
            resp_data = [{"Block":'Human detected',"Block icon":icon_str1},
            {"Block":'Hardhat not worn',"Block icon":icon_str2},
            {"Block":'Safety glasses not worn',"Block icon":icon_str3},
            {"Block":'Closed toed shoes not worn',"Block icon":''},
            {"Block":'Gloves not worn',"Block icon":''},
            {"Block":'Spill detected',"Block icon":''},
            {"Block":'Coupling breakage detected',"Block icon":''},
            {"Block":'Hearing protection not worn',"Block icon":''}]
            return json.dumps(resp_data)
        else :
            return "Error"

class populate_location:
    def GET(self):
        resp_data = [{"Location":'Shopfloor'},{"Location":'Entry hall 1'},{"Location":'Entry hall 2'}]
        return json.dumps(resp_data)

class populate_cctv:
    def GET(self):
        resp_data = [{"CCTV":'1'},{"CCTV":'2'},{"CCTV":'3'}]
        return json.dumps(resp_data)

class populate_type:
    def GET(self):
        resp_data = [{"Event type":'all'},{"Event type":'Human detected'},{"Event type":'Hard hat not worn'},
        {"Event type":'Safety glasses missing'},{"Event type":'Closed toed shoes not worn'},
        {"Event type":'Gloves not worn'},{"Event type":'Spill detected'},{"Event type":'Coupling breakage detected'}]
        return json.dumps(resp_data)

class recent_alerts:
    def GET(self):
        client_input = web.input()
        location_id = client_input.l_id
        cctv_id = client_input.cc_id
        event_type = client_input.type
        t_start = client_input.t_start
        t_end = client_input.t_end

        time_start = time_stamp(t_start)
        time_end = time_stamp(t_end)

        if event_type == 'all':
            cursor = alerts.find({"$and":[{"alert":True},{"condition":True},{"timestamp":{"$gt":time_start,"$lt":time_end}}]},{'_id': False,'condition': False,'cc_id':False,'alert':False})
            j=[]
            for alert in cursor:
                #print(alert)
                alert['timestamp'] = datetime.datetime.fromtimestamp(int(alert['timestamp']+19800)).strftime('%d-%m-%Y %H:%M:%S')
                j.append(alert)
            return json.dumps(j)
        else:
            cursor = alerts.find({"$and":[{"alert":True},{"condition":True},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]},{'_id': False,'condition': False,'cc_id':False,'alert':False})
            j=[]
            for alert in cursor:
                #print(alert)
                alert['timestamp'] = datetime.datetime.fromtimestamp(int(alert['timestamp']+19800)).strftime('%d-%m-%Y %H:%M:%S')
                j.append(alert)
            return json.dumps(j)


print("Server Started at:")

if __name__ == "__main__":

    app.run()