'''
 job alio에서 정보통신 부분만 파싱해서 db에 저장하는 코드
 3시간에 한번씩 db 초기화 후 삽입
'''
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql

today = datetime.today().strftime('%Y.%m.%d')
year = today.split('.')[0]
day = today.split('.')[2]
inputs = []
code = 'R600020' #정보통신
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"

def DB_insert(inputs):
    conn = pymysql.connect(host='localhost', user='root', password='', db='company')
    try:
        with conn.cursor() as curs:
            query = 'insert into companies (title,comp_name,place,s_date,e_date,state,url) values (%s, %s, %s, %s, %s, %s, %s)'
            curs.execute(query, (inputs))
        conn.commit()
    finally:
        conn.close()
        
def DB_truncate():
    conn = pymysql.connect(host='localhost', user='root', password='', db='company')
    try:
        with conn.cursor() as curs:
            query = 'truncate table companies'
            curs.execute(query)
        conn.commit()
    finally:
        conn.close()

headers = {"Referer":"https://job.alio.go.kr/recruit.do",
          "User-Agent": user_agent}
DB_truncate()

for i in range(1,8):
    url = "https://job.alio.go.kr/recruit.do?pageNo="+str(i)+"&param=&search_yn=Y&idx=&recruitYear=&recruitMonth=&detail_code="+code+"&e_date="+today+"&org_name=&title=&order=REG_DATE"
    html = requests.get(url,headers = headers)
    data = BeautifulSoup(html.text,'html.parser')
    row = data.find('table', class_='tbl type_03').find('tbody').find_all('tr')
    for r in row:
        column = r.find_all('td')
        idx = column[2].find('a')['id'].split('_')[1]
        column = column[2:5]+column[6:9]
        for j in column:
            j = j.text
            j = ' '.join(j.split())
            inputs.append(j)
        inside_url = 'https://job.alio.go.kr/mobile/recruitview.do?pageNo='+str(i)+'&idx='+idx+'&search_yn=&location=&detail_code=&title='
        inputs.append(inside_url)
        DB_insert((inputs))
        inputs = []
    time.sleep(3)
    headers = {"Referer":url,
              "User-Agent": user_agent}
