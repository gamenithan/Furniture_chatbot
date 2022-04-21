"""dafsf"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet1 = client.open("Chatbot-Fur").worksheet('sheet1')
order_sheet = client.open("Chatbot-Fur").worksheet('order') # เป็นการเปิดไปยังหน้าชีตนั้นๆ
def main():
    """dsfsdf"""
    cell=order_sheet.col_values(2)
    cell2=order_sheet.col_values(20)
    # lst = ["123456", "2022041023488786", "2022041023488786", "2022041123534724", "2022041123534724", "2022041123534724", "2022041123534724","sdasdasdww", "sdasasdas", "sdasasdas"]
    temp = []
    temp2 = []
    id_list = []
    name_list = []
    answer = []
    num = 0
    for i in cell:
        if num == 0:
            temp.append(cell[num])
            temp2.append(cell2[num])
            num += 1
        elif len(cell) == num+1:
            if cell[num] == cell[num-1]:
                temp.append(cell[num])
                temp2.append(cell2[num])
                id_list.append(temp)
                name_list.append(temp2)
                num += 1
            else:
                id_list.append(temp)
                name_list.append(temp2)
                temp = []
                temp2 = []
                temp.append(cell[num])
                temp2.append(cell2[num])
                num += 1
        else:
            if cell[num] == cell[num-1]:
                temp.append(cell[num])
                temp2.append(cell2[num])
                num += 1
            else:
                if len(temp) != 1:
                    id_list.append(temp)
                    name_list.append(temp2)
                temp = []
                temp2 = []
                temp.append(cell[num])
                temp2.append(cell2[num])
                num += 1
    
    a = TransactionEncoder()
    a_data = a.fit(name_list).transform(name_list)
    df = pd.DataFrame(a_data,columns=a.columns_)
    df = df.replace(False,0)
    df = apriori(df, min_support = 0.2, use_colnames = True, verbose = 1)
    print(df)
    df_ar = association_rules(df, metric = "confidence", min_threshold = 0.6)
    # print(id_list)
    # print(name_list)
    # print(len(id_list))
    print(len(name_list))
    data = list(df_ar["consequents"])
    print(df_ar)
    for i in data:
        promo_list = list(i)
        answer.append(promo_list[0])
    # print([list(x) for x in data])
    print(answer)
    
main()