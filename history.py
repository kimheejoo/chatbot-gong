import requests
from bs4 import BeautifulSoup
import pymysql

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
headers = {'Referer':'http://www.historyexam.go.kr/pst/list.do?bbs=noti',
          'User-Agent':user_agent}

def DB_truncate():
    conn = pymysql.connect(host='localhost', user='root', password='rlagmlwn', db='test')
    try:
        with conn.cursor() as curs:
            query = 'truncate table history'
            curs.execute(query)
        conn.commit()
    finally:
        conn.close()
        
def DB_insert(insert_data):
    conn = pymysql.connect(host='localhost', user='root', password='rlagmlwn', db='test')
    try:
        with conn.cursor() as curs:
            query = 'insert into history (name, regist, test, announce) values (%s, %s, %s, %s)'
            curs.execute(query,(insert_data))
        conn.commit()
    finally:
        conn.close()
        
url = 'http://www.historyexam.go.kr/pst/view.do?bbs=noti&pst_sno=1000029601&pageIndex=1&searchCondition=pstTitle&searchKeyword=&pageUnit=10'
html = requests.post(url, headers = headers)
data = BeautifulSoup(html.text,'html.parser')
# html = open('page.html')
# data = BeautifulSoup(html,'html.parser')
rows = data.select('tbody > tr')[4].select('td > div > div > table')[0].select('tbody > tr')
DB_truncate()
insert_data = []
for i in range(1,len(rows)):
    row = rows[i].select('td > p')
    for j in row:
        insert_data.append(j.text)
    DB_insert(insert_data)
    insert_data = []

