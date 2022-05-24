#codeรอปรับให้เข้ากับ project
#Import Library
import json
import os
from re import A, I
from flask import Flask
from flask import request
from flask import make_response

from PIL import Image
import requests
from io import BytesIO

from datetime import datetime

#ส่วนของการเก็บข้อมูล
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet1 = client.open("Chatbot-Fur").worksheet('sheet1')
sheet2 = client.open("Chatbot-Fur").worksheet('Inventory')
sheet3 = client.open("Chatbot-Fur").worksheet('DisplayName')
asso = client.open("Association").worksheet('Association')
promotion_list = client.open("Chatbot-Fur").worksheet('Promotion')
order_sheet = client.open("Chatbot-Fur").worksheet('order') # เป็นการเปิดไปยังหน้าชีตนั้นๆ
# pprint(data)
#-------------------------------------

#----เชื่อมต่อfirebase----
from random import randint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("chatbot-fur-firebase-adminsdk-6657a-e04847c52a.json")
firebase_admin.initialize_app(cred)
#-------------------------------------

# Flask
app = Flask(__name__)
@app.route('/', methods=['POST']) 

def MainFunction():

    #รับ intent จาก Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)
    # print(json.dumps(question_from_dailogflow_raw, indent=4 ,ensure_ascii=False))
    print(type(question_from_dailogflow_raw))
    #เรียกใช้ฟังก์ชัน generate_answer เพื่อแยกส่วนของคำถาม
    answer_from_bot = generating_answer(question_from_dailogflow_raw)
    
    #ตอบกลับไปที่ Dailogflow
    print(answer_from_bot)
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #การตั้งค่าประเภทของข้อมูลที่จะตอบกลับไป

    return r

def generating_answer(question_from_dailogflow_dict):

    #Print intent ที่รับมาจาก Dailogflow
    # print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))
    print(question_from_dailogflow_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"])
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))
    # fur = question_from_dailogflow_dict["queryResult"]["outputContexts"][1]["parameters"]["Fur.original"]
    print("--------------")
    #เก็บต่า ชื่อของ intent ที่รับมาจาก Dailogflow
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"]
    num = 0
    #ลูปตัวเลือกของฟังก์ชั่นสำหรับตอบคำถามกลับ
    if intent_group_question_str == 'คำนวนข้อมูลสินค้า':
        answer_str = question_Furniture_data(question_from_dailogflow_dict)
    elif intent_group_question_str == 'คำนวนสินค้าในสต็อก': 
        answer_str = check_stock(question_from_dailogflow_dict)
    elif intent_group_question_str == 'โปรโมชั่นแนะนำ': 
        answer_str = promotion(question_from_dailogflow_dict)
    elif intent_group_question_str == 'ราคาสินค้า':
        answer_str = check_price()
    elif intent_group_question_str == 'แนะนำสินค้า':
        answer_str = recommend_item(question_from_dailogflow_dict)
    elif intent_group_question_str == 'ขอดูรูป':
        num = 1
        answer_str = check_img()
    elif intent_group_question_str == 'รูป':
        num = 1
        answer_str = test_img(question_from_dailogflow_dict)
    else: answer_str = "ผมไม่เข้าใจ คุณต้องการอะไร"

    #สร้างการแสดงของ dict 
    # answer_from_bot = {"fulfillmentMessages": [{"platform": "LINE","image": {"imageUri": "https://www.ikea-club.org/images/productcatalog/gallery/S69276421/1.jpg"}}]}
    if num == 1:
        answer_from_bot = {"fulfillmentMessages": answer_str}
    else:
        answer_from_bot = {"fulfillmentText": answer_str}
    # answer_from_bot = {"line": {"previewImageUrl": "https://www.ikea-club.org/images/productcatalog/gallery/S69276421/1.jpg", "originalContentUrl": "https://www.ikea-club.org/images/productcatalog/gallery/S69276421/1.jpg", "type": "image"}}
    
    #แปลงจาก dict ให้เป็น JSON
    # answer_from_bot = json.dumps(answer_from_bot, indent=4)
    
    return answer_from_bot

def question_Furniture_data(respond_dict):
    fur = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["Fur.original"].upper()
    userid = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    timestamp = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["timestamp"]
    print(int(timestamp))
    timestamp2 = datetime.fromtimestamp(int(timestamp)/1000)
    cell=sheet2.col_values(4)
    num = 1
    line_bot_api = LineBotApi('hV/ADGn/G8L1r6E2BGTH3ShT+UH2YxZY2JA7TsdDeqxizdeMuJ1ghDkpYmBy0rYGmi+2RnREJuimUpC1DCTSYcuDp+Hf1kborFKHRMYkGpqdxCJGzb2e85TF0hv6+4zHrA5XUDQcKNikdcoV1LEgGwdB04t89/1O/w1cDnyilFU=')
    profile = line_bot_api.get_profile(userid)
    profile = json.loads(str(profile))
    dis_name = profile["displayName"]
    # sheet.insert_row([fur], 2)
    for i in cell:
        dict_name = i.split()
        if str(fur) in dict_name:
            Item_name = sheet2.cell(num, 2).value
            Item_type = sheet2.cell(num, 5).value
            Item_price = sheet2.cell(num, 9).value
            Item_des = sheet2.cell(num, 8).value
            Item_stock = sheet2.cell(num, 12).value
            item_link = sheet2.cell(num, 16).value
            answer_function = "สินค้าชื่อ: " + Item_name + "\n" + "รายละเอียดสินค้า: " + Item_type + Item_des + "\n" + "ราคาสินค้า: " + Item_price + " บาท\n" +  "สินค้าคงเหลือ: " + Item_stock + \
                " ชิ้น "   + "\nหากสนใจสั่งซื้อได้ที่ " + item_link
            sheet1.insert_row([userid, timestamp2.strftime("%Y-%m-%d %H:%M:%S"), fur, dis_name], 2)
            break
        elif i == None:
            answer_function = "ไม่มีข้อมูลหรือคุณอาจเขียนชื่อสินค้าไม่ถูกต้อง"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูลหรือคุณอาจเขียนชื่อสินค้าไม่ถูกต้อง"
    return answer_function

def check_stock(respond_dict): 
    fur = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["fur.original"].upper()
    cell=sheet2.col_values(4)
    num = 1
    for i in cell:
        dict_name = i.split()
        if str(fur) in dict_name:
            Item_name = sheet2.cell(num, 12).value
            answer_function = "จำนวนสินค้ามีทั้งหมด" + ' ' + Item_name + ' ' + "ชิ้น"
            break
        elif i == None:
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def check_price():
    fur = sheet1.cell(2, 3).value.upper()
    cell=sheet2.col_values(4)
    num = 1
    for i in cell:
        dict_name = i.split()
        if str(fur) in dict_name:
            Item_name = sheet2.cell(num, 9).value
            answer_function = "ราคา"+ ' ' + Item_name + ' ' + "บาท"
            break
        elif i == None:
            # Item_name = sheet.cell(3,15).value
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function


def check_img():
    fur = sheet1.cell(2, 3).value.upper()
    cell= sheet2.col_values(4)
    num = 1
    for i in cell:
        dict_name = i.split()
        if str(fur) in dict_name:
            Item_name = sheet2.cell(num, 6).value
            answer_function = [{"platform": "LINE","image": {"imageUri": Item_name}}]
            break
        elif i == None:
            # Item_name = sheet.cell(3,15).value
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def test_img(respond_dict): 
    img = {"line": {"type": "text","text": "สวัสดี นี่คือคำทักทายจาก Dialogflow (Custom payload)"}}
    # answer_function = json.dumps(img, indent=4)
    
    return img

def recommend_item(respond_dict):
    answer_function = ""
    cell1=order_sheet.col_values(2)
    cell2=order_sheet.col_values(20)
    inven = sheet2.col_values(2)
    temp = []
    temp2 = []
    id_list = []
    name_list = []
    post_list = []
    pre_list = []
    count = 0
    name = " "
    for i in cell1:
        if count == 0:
            temp.append(cell1[count])
            temp2.append(cell2[count])
            count += 1
        elif len(cell1) == count+1:
            if cell1[count] == cell1[count-1]:
                temp.append(cell1[count])
                temp2.append(cell2[count])
                id_list.append(temp)
                name_list.append(temp2)
                count += 1
            else:
                id_list.append(temp)
                name_list.append(temp2)
                temp = []
                temp2 = []
                temp.append(cell1[count])
                temp2.append(cell2[count])
                count += 1
        else:
            if cell1[count] == cell1[count-1]:
                temp.append(cell1[count])
                temp2.append(cell2[count])
                count += 1
            else:
                if len(temp) != 1:
                    id_list.append(temp)
                    name_list.append(temp2)
                temp = []
                temp2 = []
                temp.append(cell1[count])
                temp2.append(cell2[count])
                count += 1
    
    a = TransactionEncoder()
    a_data = a.fit(name_list).transform(name_list)
    df = pd.DataFrame(a_data,columns=a.columns_)
    df = df.replace(False,0)
    df = apriori(df, min_support = 0.2, use_colnames = True, verbose = 1)
    df_ar = association_rules(df, metric = "confidence", min_threshold = 0.6)
    data = list(df_ar["consequents"])
    for i in data:
        promo_list = list(i)
        post_list.append(promo_list[0])
    pre = list(df_ar["antecedents"])
    for i in pre:
        promo_list = list(i)
        pre_list.append(promo_list[0])
    print(pre_list)
    print(post_list)
    check_id = sheet1.col_values(1)
    search_his = sheet1.col_values(3)
    count = 0
    item_his = []
    userid = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    for i in check_id:
        if i == userid:
            # print(count)
            # print(search_his[count])
            if search_his[count] in pre_list:
                # print('test')
                item_his.append(search_his[count])
            pass
        elif i == None:
            pass
        else:
            pass
        count += 1
    print(item_his)
    count2 = 0
    count3 = 0
    answer = "ไม่มีข้อมูล"
    counter = 0
    for i in item_his:
        temp = item_his.count(i)
        if temp > counter:
            counter = temp
            answer = i
    print(answer)
    for i in pre_list:
        print(i + str(count2))
        print(answer + str(count2))
        if i == answer:
            count3 += 1
            answer = post_list[count2]
            print(answer)
            break
        count2 += 1
    num = 1

    for i in inven:
        if i == answer:
            name = sheet2.cell(num, 4).value
            item_link = sheet2.cell(num, 16).value
            break
        else:
            answer_function = "ไม่มีข้อมูล"
        num += 1
    
    if name != " ":
        answer_function = "คุณอาจสนใจ " + name + " \nสามารถดูรายละเอียดได้ที่\n" + item_link
    else:
        answer_function = "สินค้าขายดีแนะนำ\n" + "https://shop.line.me/@224zwhrr/collection/73765"
        
    return answer_function

# def type_item(respond_dict):
#     print(respond_dict)
#     type_data = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["type.original"]
#     cell=sheet2.col_values(5)
#     num = 1
#     for i in cell:
#         if type_data in i:
#             item_link = sheet2.cell(num, 16).value
#             answer_function = item_link
#             break
#         elif i == None:
#             answer_function = "ไม่มีข้อมูล"
#         else:
#             num += 1
#             answer_function = "ไม่มีข้อมูล"
#     return answer_function

def promotion(respond_dict):
    userid = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    line_bot_api = LineBotApi('hV/ADGn/G8L1r6E2BGTH3ShT+UH2YxZY2JA7TsdDeqxizdeMuJ1ghDkpYmBy0rYGmi+2RnREJuimUpC1DCTSYcuDp+Hf1kborFKHRMYkGpqdxCJGzb2e85TF0hv6+4zHrA5XUDQcKNikdcoV1LEgGwdB04t89/1O/w1cDnyilFU=')
    profile = line_bot_api.get_profile(userid)
    profile = json.loads(str(profile))
    dis_name = profile["displayName"]
    cell = order_sheet.col_values(7)
    item = order_sheet.col_values(20)
    promotion = promotion_list.col_values(2)
    pre = asso.col_values(2)
    post = asso.col_values(3)
    order_list = []
    num = 0
    num2 = 0
    num3 = 1
    name = " "
    answer_function = ""
    for i in cell:
        if dis_name == i:
            order_list.append(item[num])
        num += 1
    check = 0
    order_list = list(dict.fromkeys(order_list))
    for i in pre:
        i = i.replace("frozenset({'", '')
        i = i.replace("'})", '')
        for j in order_list:
            if j == i:
                answer_function = post[num2].replace("frozenset({'", '')
                answer_function = answer_function.replace("'})", '')
                if answer_function in order_list:
                    answer_function = "ยังไม่มีโปรโมชั่นแนะนำสำหรับคุณ"
                    continue
                pre_name = pre[num2].replace("frozenset({'", '')
                pre_name = pre_name.replace("'})", '')
                break
            else:
                pre_name = ""
                answer_function = "ยังไม่มีโปรโมชั่นแนะนำสำหรับคุณ"
        num2 += 1
    for i in promotion:
        if i == answer_function:
            item_link = promotion_list.cell(num3, 16).value
            name = promotion_list.cell(num3, 4).value
            break
        num3 += 1
    if name != " ":
        answer_function = "เนือกจากคุณเคยสั่ง " + pre_name + "\nเราเลยแนะนำสินค้าที่คุณอาจสนใจชื่อ \n" + name + " เนื่องจากมีโปรโมชั่นอยู่ \nสามารถดูรายละเอียดได้ที่ \n" + item_link
    else:
        answer_function = "โปรโมชั่นทั้งหมด\n" + "https://shop.line.me/@224zwhrr/collection/73765"
    return answer_function

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
# {"type": "bubble","direction": "ltr","header": {"type": "box","layout": "vertical","contents": [  {   "type": "text",    "text": "Header",    "align": "center",    "contents": []  }]},"hero": {"type": "image","url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png","size": "full","aspectRatio": "1.51:1","aspectMode": "fit" },"body": {"type": "box","layout": "vertical","contents": [{"type": "text","text": "Body","align": "center","contents": []}]},"footer": {"type": "box","layout": "horizontal","contents": [{"type": "button","action": {"type": "uri","label": "Button","uri": "https://linecorp.com"}}]}}