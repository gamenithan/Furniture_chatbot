#codeรอปรับให้เข้ากับ project
#Import Library
import json
import os
from re import I
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

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet1 = client.open("Chatbot-Fur").worksheet('sheet1')
sheet2 = client.open("Chatbot-Fur").worksheet('sheet2') # เป็นการเปิดไปยังหน้าชีตนั้นๆ
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
    # userid = question_from_dailogflow_raw["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    # cell_name = sheet1.col_values(1)
    # num = 1
    # for i in cell_name:
    #     if i == userid:
    #         num = 0
    #         break
    # if num == 1:
    #     sheet1.insert_row([userid], 2)
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
    elif intent_group_question_str == 'ราคาสินค้า':
        answer_str = check_price()
    elif intent_group_question_str == 'ดีไซเนอร์': 
        answer_str = check_designer()
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
    fur = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["Fur.original"]
    userid = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    timestamp = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["timestamp"]
    print(int(timestamp))
    timestamp2 = datetime.fromtimestamp(int(timestamp)/1000)
    # database_ref = firestore.client().document('Furniture/Item_list')
    # database_dict = database_ref.get().to_dict()
    # database_list = list(database_dict.values())
    # ran_menu = randint(0, len(database_list)-1)
    # menu_name = database_list[ran_menu]
    cell=sheet2.col_values(3)
    num = 1
    # sheet.insert_row([fur], 2)
    for i in cell:
        if str(i) == str(fur):
            Item_name = sheet2.cell(num, 10).value
            Item_price = sheet2.cell(num, 5).value
            Item_designer = sheet2.cell(num, 11).value
            Item_stock = sheet2.cell(num, 16).value
            answer_function = "สินค้าชื่อ: " + fur + "\n" + "รายละเอียดสินค้า: " + Item_name + "\n" + "ราคาสินค้า: " + Item_price + " บาท\n" + "ดีไซเนอร์ชื่อ: " + Item_designer + "\n" + "สินค้าคงเหลือ: " + Item_stock + \
                " ชิ้น"
            sheet1.insert_row([userid, timestamp2.strftime("%Y-%m-%d %H:%M:%S"), fur], 2)
            break
        elif i == None:
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def check_stock(respond_dict): 
    fur = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["fur.original"]
    cell=sheet2.col_values(3)
    num = 1
    for i in cell:
        if str(i) == str(fur):
            Item_name = sheet2.cell(num, 16).value
            answer_function = "จำนวนสินค้ามีทั้งหมด" + ' ' + Item_name + ' ' + "ชิ้น"
            break
        elif i == None:
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def check_price():
    fur = sheet1.cell(2, 3).value
    cell=sheet2.col_values(3)
    num = 1
    for i in cell:
        if str(i) == str(fur):
            Item_name = sheet2.cell(num, 5).value
            answer_function = "ราคา"+ ' ' + Item_name + ' ' + "บาท"
            break
        elif i == None:
            # Item_name = sheet.cell(3,15).value
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def check_designer():
    fur = sheet1.cell(2, 3).value
    cell=sheet2.col_values(3)
    num = 1
    for i in cell:
        if str(i) == str(fur):
            Item_name = sheet2.cell(num, 11).value
            answer_function = "ดีไซเนอร์ชื่อ"+ ' ' + Item_name
            break
        elif i == None:
            # Item_name = sheet.cell(3,15).value
            answer_function = "ไม่มีข้อมูล"
        else:
            num += 1
            answer_function = "ไม่มีข้อมูล"
    return answer_function

def check_img():
    fur = sheet1.cell(2, 3).value
    cell=sheet2.col_values(3)
    num = 1
    for i in cell:
        if str(i) == str(fur):
            Item_name = sheet2.cell(num, 15).value
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
    img = [{"platform": "LINE","image": {"imageUri": "https://www.ikea-club.org/images/productcatalog/gallery/S69276421/1.jpg"}}]
    # answer_function = json.dumps(img, indent=4)
    
    return img

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
