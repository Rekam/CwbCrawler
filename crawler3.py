from selenium.webdriver.support.ui import Select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import date
from dateutil.rrule import rrule, DAILY, WEEKLY
import os
from enum import Enum

        
class cwb:
    def __init__(self):
        self.browser = None
        self.downloadFolder = ""
        self.counties = []
        self.allStations = []
        self.dataClass = {}
        self.dataType = {}
    ### 
    ### 瀏覽器相關
    ###
    
    # 開啟瀏覽器
    def openBrowser(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory':self.downloadFolder}
        chrome_options.add_experimental_option('prefs', prefs)
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.browser.get("https://e-service.cwb.gov.tw/HistoryDataQuery/index.jsp")
        time.sleep(2)
    # 取得所有Select內容
    def getAllSelect(self):
        if self.browser is not None:
            self.__getAllCounties()
            self.__getAllStations()
            self.__deleteUnnecessaryStation()
            self.__getAllDataClass()
            self.__getAllDatatype()
        else:
            print('Please Open Browser!!!')
    # 取得所有城市
    def __getAllCounties(self):
        select_stationCounty = Select(self.browser.find_element_by_id("stationCounty"))
        self.counties.clear()
        for option in select_stationCounty.options:
                #print('key = ',option.get_attribute('value'),'// value =',option.text)
                self.counties.append(option.get_attribute('value'))
        return self.counties
    # 取得城市所有測站
    def __getAllStationAtCounty(self, county):
        # selectCounty first
        select_stationCounty = Select(self.browser.find_element_by_id("stationCounty"))
        select_stationCounty.select_by_value(county)
        select_station = Select(self.browser.find_element_by_name("station"))
        stations = {}
        for option in select_station.options:
                #print('key = ',option.get_attribute('value'),'// value =',option.text)
                stations[option.get_attribute('value')] = option.text
        return stations
    # 取得所有測站
    def __getAllStations(self):
        self.allStations.clear()
        totalCounties = len(self.counties)
        for county in self.counties:
            #print(county)
            countyIndex = self.counties.index(county)
            self.allStations.append(self.__getAllStationAtCounty(county))
            print(f'loading({countyIndex+1}/{totalCounties}) - {county}')
    # 移除撤銷站        
    def __deleteUnnecessaryStation(self):
        totalDelete = 0
        totalStations = 0
        for county in self.counties:
            stationsAtCounty = self.allStations[self.counties.index(county)]
            deleteStations = []
            deleteStationsName = []
            for station in stationsAtCounty.items():
                # print(station[1])
                if "撤銷站" in station[1]:
                    deleteStations.append(station[0])
                    deleteStationsName.append(station[1])
            totalDelete = totalDelete + len(deleteStationsName)
            print(f'{county} 測站 ({len(stationsAtCounty)}/{len(deleteStationsName)}/{len(stationsAtCounty)-len(deleteStationsName)})')
            for delete in deleteStations:
                #print('刪除',delete)
                del self.allStations[self.counties.index(county)][delete]
            totalStations = totalStations + len(self.allStations[self.counties.index(county)])
        print(f'全國總測站數量={totalDelete}')
        print(f'全國撤銷站數量={totalStations}')
    # 取得資料類型    
    def __getAllDataClass(self):
        select_dataclass = Select(self.browser.find_element_by_name("dataclass"))
        self.dataClass.clear()
        for option in select_dataclass.options:
                #print('key = ',option.get_attribute('value'),'// value =',option.text)
                self.dataClass[option.get_attribute('value')] = option.text
    # 取得資料型態            
    def __getAllDatatype(self):
        select_datatype = Select(self.browser.find_element_by_name("datatype"))
        self.dataType.clear()
        for option in select_datatype.options:
                #print('key = ',option.get_attribute('value'),'// value =',option.text)
                self.dataType[option.get_attribute('value')] = option.text
    
    
    ### 
    ### 處理下載相關
    ###
    # 下載測站list的資料
    def downloadList(self, TargetList, start_date, end_date):
        target_index_List = self.__check_dir(TargetList)
        #print(targetList_index)
        base_dir = self.downloadFolder
        for target_index in target_index_List:
            county_index = target_index[0]
            station_key = target_index[1]
            county = self.counties[county_index]
            station = self.allStations[county_index][station_key]
            # 先關閉原本browser
            try:
                self.browser.close()
            except:
                print("browser closed")
            station_dir = os.path.join(base_dir,f'{county}_{station}_{station_key}')
            self.downloadFolder = station_dir
            self.openBrowser()
            print(target_index[0],type(target_index[0]))
            print(target_index[1],type(target_index[1]))
            self.__downloadDateRange(county_index, station_key, start_date, end_date)
        
    # 檢查資料夾,若無則建立
    def __check_dir(self, stations):
        base_dir = self.downloadFolder
        target_index = []
        for target in stations:
            for county in self.counties:
                #county_dir =os.path.join(base_dir,county)
                dictionary = self.allStations[self.counties.index(county)]
                for station in dictionary.items():
                    #print(station[1])
                    if target in station[1]:
                        target = station[1]
                        print(target+' at '+county)
                        station_dir = os.path.join(base_dir,f'{county}_{station[1]}_{station[0]}')
                        self.__create_dir(station_dir)
                        target_index.append((self.counties.index(county),station[0]))
        return target_index
    
    def __create_dir(self, dirPath):
        if os.path.isdir(dirPath):
            print("資料夾存在")
        else:
            print("資料夾不存在，創建新的")
            os.makedirs(dirPath)
    
    # 檢查所有資料夾是否存在
    def __checkAll_dir(self):
        base_dir = self.downloadFolder
        for county in self.counties:
            #county_dir =os.path.join(base_dir,county)
            #print(county_dir)
            dictionary = self.allStations[self.counties.index(county)]
            for station in dictionary.items():
                station_dir = os.path.join(base_dir,f'{county}_{station[1]}_{station[0]}')
                print(station_dir)
                # 檢查資料夾 若不存在則建立一下 :)
                self.__create_dir(station_dir)
    
    def __downloadDateRange(self, countyIndex, stationKey, start_date, end_date):
        for dt in rrule(DAILY, dtstart=start_date, until=end_date):
            print(dt.date())
            self.__downloadDate(countyIndex, stationKey, dt.date()) 
    
    def __downloadDate(self, countyIndex, stationKey, date):
        self.__setAllDate(self.counties[countyIndex], stationKey ,list(self.dataClass)[0],list(self.dataType)[0], date.isoformat())
        self.browser.execute_script("arguments[0].click();",self.browser.find_element_by_xpath("//img[@src='images/serch.jpg']"))
        time.sleep(2)
        self.browser.switch_to.window(self.browser.window_handles[1])
        self.browser.find_element_by_id("downloadCSV").click()
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])
        time.sleep(2)
        fileName = self.__getDownLoadedFileName()
    
    def __setAllDate(self,county, station, dataClass, dataType,  date):
        # county
        select_stationCounty = Select(self.browser.find_element_by_id("stationCounty"))
        select_stationCounty.select_by_value(county)
        # station
        select_station = Select(self.browser.find_element_by_name("station"))
        select_station.select_by_value(station)
        # dataClass
        select_dataclass = Select(self.browser.find_element_by_name("dataclass"))
        select_dataclass.select_by_value(dataClass)
        # dataType
        select_datatype = Select(self.browser.find_element_by_name("datatype"))
        select_datatype.select_by_value(dataType)
        self.browser.find_element_by_xpath("//input[@class='text2 hasDatepicker' and @id='datepicker']").clear()
        self.browser.find_element_by_xpath("//input[@class='text2 hasDatepicker' and @id='datepicker']").send_keys(date)
    
    
    def __getDownLoadedFileName(self):
        # open a new tab
        self.browser.execute_script("window.open()")
        # switch to new tab
        self.browser.switch_to.window(self.browser.window_handles[-1])
        # navigate to chrome downloads
        self.browser.get('chrome://downloads')
        # get the latest downloaded file name
        fileName = self.browser.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
        # get the latest downloaded file url
        sourceURL = self.browser.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').href")
        # print the details
        print(fileName)
        #print (sourceURL)
        # close the downloads tab2
        self.browser.close()
        # switch back to main window
        self.browser.switch_to.window(self.browser.window_handles[0])
        return fileName
    
    
# 測試資料庫 若沒有檔案會自己建立 data/cwbStations.db
import sqlite3
import os

class sqlDB:
    def __init__(self, dbName):
        # 建立資料夾 若不存在的話
        
        self.__create_dir('data')
        self.conn = sqlite3.connect(os.path.join('data', f"{dbName}.db"))
        print("Database Opened successfully")
        # 建立cursor變數
        self.cursorObj = self.conn.cursor()
        # 先檢查是否表格存在，若不存在的話，則建立表格
        if self.__checkTableExist("county") is False:
            self.__createCountyTable("county")
        
        
    def __create_dir(self, dirPath):
        if os.path.isdir(dirPath):
            print("資料夾存在")
        else:
            print("資料夾不存在，創建新的")
            os.makedirs(dirPath)
    
    def __createCountyTable(self, tableName):
        self.cursorObj.execute(f"CREATE TABLE {tableName} (countyName TEXT, countyIndex INTEGER, PRIMARY KEY(countyIndex))")
        print(f'{tableName}, Table created')
        
    def checkTableEmpty(self, tableName):
        try:
            count = self.cursorObj.execute(f"select count(*) from {tableName} Limit 1")
            number = count.fetchall()[0][0]
            if number == 0:
                print('Table is empty')
            else:
                print(f'Table row count is {number}')
        except:
            print('可能沒這個表格唷!')
    def __checkTableExist(self, tableName):
        # 檢查資料表是否存在
        # https://pythonexamples.org/python-sqlite3-check-if-table-exists/
        #get the count of tables with the name
        self.cursorObj.execute(f" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tableName}' ")
        #if the count is 1, then table exists
        if self.cursorObj.fetchone()[0]==1:
            print(f'{tableName}, Table existed')
            exist = True
        else:
            print(f'{tableName}, Table does not exist')
            exist = False    
        return exist    
        
    def closeDB(self):
        self.cursorObj.close()
        print("Database Closed successfully")
    
    
        
    
            
    
    
    
                
    
    

    
    
    
    
    
