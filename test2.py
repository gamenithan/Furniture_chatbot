# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from pprint import pprint
# from test import *
# import pandas as pd
# import numpy as np
# from mlxtend.frequent_patterns import apriori, association_rules
# from mlxtend.preprocessing import TransactionEncoder
# scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
# cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
# client = gspread.authorize(cerds)
# sheet1 = client.open("Chatbot-Fur").worksheet('sheet1')
# sheet2 = client.open("Chatbot-Fur").worksheet('order') # เป็นการเปิดไปยังหน้าชีตนั้นๆ
from cgi import test
import requests
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet1 = client.open("Chatbot-Fur").worksheet('sheet1')
sheet2 = client.open("Chatbot-Fur").worksheet('DisplayName')
order_sheet = client.open("Chatbot-Fur").worksheet('order') # เป็นการเปิดไปยังหน้าชีตนั้นๆ

def main2():
    line_bot_api = LineBotApi('hV/ADGn/G8L1r6E2BGTH3ShT+UH2YxZY2JA7TsdDeqxizdeMuJ1ghDkpYmBy0rYGmi+2RnREJuimUpC1DCTSYcuDp+Hf1kborFKHRMYkGpqdxCJGzb2e85TF0hv6+4zHrA5XUDQcKNikdcoV1LEgGwdB04t89/1O/w1cDnyilFU=')
    profile = line_bot_api.get_profile('Udae72953b84b9e29cbff8180b8c9f841')
    profile = json.loads(str(profile))
    print(profile["displayName"])
def test1():
    cell = order_sheet.col_values(7)
    item = order_sheet.col_values(20)
    disname = sheet2.cell(2, 1).value
    order_list = []
    num = 0
    for i in cell:
        if disname == i:
            order_list.append(item[num])
        num += 1
    print(order_list)

test1()