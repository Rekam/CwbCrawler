#!/usr/bin/env python
# coding: utf-8

# 檢查bs4安裝路徑
import bs4 
print(bs4.__file__)

# In[4]:

# 參考 https://ericjhang.github.io/archives/dad03d64.html
# 參考 https://wreadit.com/@wwwlearncodewithmikecom/post/151826
# 參考 https://leemeng.tw/beautifulsoup-cheat-sheet.html

# 2021.03.31
# target: https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx
# post method

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import date
from dateutil.rrule import rrule, DAILY, WEEKLY

class Water:
    # 初始化 開啟網站
    def __init__(self, *Reservoir):
        self.Reservoir = Reservoir
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.get("https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx")
        # print(self.Reservoir[0])
    
    # 抓取每日每小時的Dataframe
    def daily (self, year, month, day, hour, minute):
        select_year = Select(self.browser.find_element_by_name("ctl00$cphMain$ucDate$cboYear"))
        select_year.select_by_value(year)  # 選擇傳入的年份
        select_month = Select(self.browser.find_element_by_name("ctl00$cphMain$ucDate$cboMonth"))
        select_month.select_by_value(month)  # 選擇傳入的月份
        select_day = Select(self.browser.find_element_by_name("ctl00$cphMain$ucDate$cboDay"))
        select_day.select_by_value(day)  # 選擇傳入的日期
        
        select_hour = Select(self.browser.find_element_by_name("ctl00$cphMain$ucDate$cboHour"))
        select_hour.select_by_value(hour)  # 選擇傳入的小時
        select_minute = Select(self.browser.find_element_by_name("ctl00$cphMain$ucDate$cboMinute"))
        select_minute.select_by_value(minute)  # 選擇傳入的分鐘
        
        #browser.execute_script("document.getElementById('search').click()"")
        self.browser.find_element_by_class_name("search").click()
        time.sleep(2)
        dfs = pd.read_html(self.browser.page_source)
        # print(dfs)
        return dfs
        #soup = BeautifulSoup(browser.page_source, "lxml")
        #table = soup.find("table", {"id":"ctl00_cphMain_gvList"})
        #columns = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
        #print(columns)
        #print(table.text)
        
    # 設定日期範圍
    def date_range(self, start_date, end_date):
        return [dt.date() for dt in rrule(DAILY, dtstart=start_date, until=end_date)]
        
    def perHour(self, year, month, day):
        # 從0~23小時 (取整點) 數字轉字串
        df = pd.DataFrame()
        for i in range(5):
            dfs = self.daily(str(year),str(month),str(day),str(i),"0")
            tempDf =self.formatDf(dfs)
            if i==0:
                df = tempDf
            else:
                df=df.append(tempDf,ignore_index=True)
        return df
        
    def checkDF(self, dfs):
        # 測試處理dataframe
        # 參考: https://leemeng.tw/practical-pandas-tutorial-for-aspiring-data-scientists.html
        # 參考: https://www.learncodewithmike.com/2020/11/read-html-table-using-pandas.html
        # print(dfs)
        print("型態", type(dfs))
        print("長度", len(dfs))
        
    # 抓取網頁後 第一次格式整理    
    def formatDf(self, dfs):
        # 讀取第一個表格
        df = dfs[0]
        #print(df)
        # 看看前五筆資料
        # df.head(5) 

        # 去除尾巴
        df =df.drop(20)
        # 選取欄位當作最後欄位
        df.columns = df.columns.get_level_values(2)

        # 檢查欄位
        # df['水庫名稱']
        # 篩選所需要的rows & columns
        df = df.iloc[:,[0,1,2,3,4,5,6,7]]

        # 修改column名稱
        df.rename(columns={'水庫名稱':'水庫','水情時間':'時間', '本日集水區累積降雨量(mm)':'累積雨量(mm)'},inplace =True)

        # 篩選需要的行row
        # filter2 = (df['水庫'] == "石門水庫") | (df['水庫'] == "曾文水庫") | (df['水庫'] == "翡翠水庫")
        # filter2 = (df['水庫'] == self.Reservoir[0])

        # df = df[filter2]
        return df
        # df.set_index(['時間'])
        # 反轉行列
        #df.T

        # 查看特定column或者row
        # df.loc[0]
        #print(df)


def test(ccc):
    print(ccc)


    
    
    
    
    
    
    
    
# 撰寫UI 暫緩 (參考內容)...
import ipywidgets as widgets
from IPython.display import display

def widget(conn, table_name, crawl_func, range_date):

    date_picker_from = widgets.DatePicker(
        description='from',
        disabled=False,
    )
    
    if table_exist(conn, table_name):
        date_picker_from.value = table_latest_date(conn, table_name)
    
    date_picker_to = widgets.DatePicker(
        description='to',
        disabled=False,
    )
    
    date_picker_to.value = datetime.datetime.now().date()

    btn = widgets.Button(description='update ')
    
    def onupdate(x):
        dates = range_date(date_picker_from.value, date_picker_to.value)
        
        if len(dates) == 0:
            print('no data to parse')
            
        update_table(conn, table_name, crawl_func, dates)
    
    btn.on_click(onupdate)

    if table_exist(conn, table_name):
        label = widgets.Label(table_name + 
                              ' (from ' + table_earliest_date(conn, table_name).strftime('%Y-%m-%d') + 
                              ' to ' + table_latest_date(conn, table_name).strftime('%Y-%m-%d') + ')')
    else:
        label = widgets.Label(table_name + ' (No table found)(對於finance_statement是正常情況)')

    items = [date_picker_from, date_picker_to, btn]
    display(widgets.VBox([label, widgets.HBox(items)]))
    









