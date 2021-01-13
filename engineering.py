import requests
from bs4 import BeautifulSoup
import pymysql

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
headers = {"Referer":"http://www.q-net.or.kr/crf005.do?id=crf00503&jmCd=1320",
         "User-Agent":user_agent}

def DB_truncate():
    conn = pymysql.connect(host='localhost', user='root', password='', db='test')
    try:
        with conn.cursor() as curs:
            query = 'truncate table engineering'
            curs.execute(query)
        conn.commit()
    finally:
        conn.close()
        
def DB_insert(insert_data):
    conn = pymysql.connect(host='localhost', user='root', password='', db='test')
    try:
        with conn.cursor() as curs:
            query = 'insert into engineering (title,one_regist,one_test,one_pass,two_regist,two_test,two_pass) values (%s, %s, %s, %s, %s, %s, %s)'
            curs.execute(query,(insert_data))
        conn.commit()
    finally:
        conn.close()
        
url = 'http://www.q-net.or.kr/crf005.do?id=crf00503s02&gSite=Q&gId=&jmCd=1320&jmInfoDivCcd=B0&jmNm=%C1%A4%BA%B8%C3%B3%B8%AE%B1%E2%BB%E7'
html = requests.get(url, headers = headers)
data = BeautifulSoup(html.text,'html.parser')
rows = data.find('div',class_='tbl_normal tdCenter mb0').find('table').find('tbody').find_all('tr')

DB_truncate()

insert_data = []
for i in rows:
    row = i.find_all('td')
    for j in row:
        j = j.text
        j = ' '.join(j.split())
        insert_data.append(j)
    DB_insert(insert_data)
    insert_data = []
