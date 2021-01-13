import requests
from bs4 import BeautifulSoup
import pymysql

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
headers = {"Referer":"https://www.google.com/",
         "User-Agent":user_agent}

def DB_truncate():
    conn = pymysql.connect(host='localhost', user='root', password='', db='test')
    try:
        with conn.cursor() as curs:
            query = 'truncate table toeic'
            curs.execute(query)
        conn.commit()
    finally:
        conn.close()
        
def DB_insert(insert_data):
    conn = pymysql.connect(host='localhost', user='root', password='', db='test')
    try:
        with conn.cursor() as curs:
            query = 'insert into toeic (test,announce,regist_end, url) values (%s, %s, %s, %s)'
            curs.execute(query,(insert_data))
        conn.commit()
    finally:
        conn.close()

url = 'https://exam.toeic.co.kr/examMainAjaxType1.php'
html = requests.get(url, headers = headers)
data = BeautifulSoup(html.text,'html.parser')
span_info = data.select('span.info') 
span_date = data.select('span.date')
DB_truncate()
for i in range(5):
    insert_data = []
    date = span_date[i].text
    date = ''.join(date.split())
    insert_data.append(date)
    span = span_info[i].text
    span = ''.join(span.split())
    end = span[:23]
    announce = span[23:]
    insert_data.append(announce)
    insert_data.append(end)
    insert_data.append('https://exam.toeic.co.kr/')
    DB_insert(insert_data)
