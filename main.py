import os
import time
import sys
import requests
from bs4 import BeautifulSoup
import datetime

class lotteryError(Exception):
	def __init__(self):
		super().__init__()

	def __str__(self):
		return "lottery empty: no data found"

class main:
	# 威力彩, 大樂透, 今彩539,
	# 雙贏彩, 三星彩, 四星彩,
	# 38樂合彩, 49樂合彩, 39樂合彩
	lottery_type = [
		"lotto/superlotto638", "lotto/Lotto649", "lotto/DailyCash", 
		"Lotto1224", "Lotto/3D", "Lotto/4D", 
		"lotto/38M6", "Lotto/49M6", "Lotto/39M5"
	]
	lottery_header = [
		"SuperLotto638", "Lotto649", "D539",
		"Lotto1224", "L3D", "L4D",
		"M638", "M649", "M539"
	]
	lottery_control = {
		"SuperLotto638": "1", "Lotto649": "", "D539": "1",
		"Lotto1224" : "", "L3D": "1", "L4D": "1",
		"M638": "1", "M649": "1", "M539": "1"
	}
	lottery_dropdown = [
		1, 2, 3,
		4, 6, 7,
		8, 9, 10
	]

	def __init__(self):
		self.url_f      = "https://www.taiwanlottery.com.tw/"
		self.url_l      = "/history.aspx"
		self.useragent  = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
			"Content-Type": "application/x-www-form-urlencoded"
			}
		self.start_year = 103
		self.end_year = datetime.datetime.now().year

	def craw(self):
		for dropdown, header, element in zip(main.lottery_dropdown, main.lottery_header, main.lottery_type):
			for year in range(self.start_year, self.end_year + 1):
				counter = 105
				while True:
					tcounter = str(counter)
					prefixs = "{}Control_history1".format(header)
					myparams = {
						"{}$DropDownList1".format(prefixs): int(dropdown),
						"{}$chk".format(prefixs): "radNO",
						"{}$txtNo".format(prefixs): "{}000{}".format(year, tcounter.zfill(3)),
						"{}$btnSubmit".format(prefixs): "查詢",
					}
					myurl = "{}{}{}".format(self.url_f, element, self.url_l)
					htmlpage = requests.post(myurl, data=myparams, headers=self.useragent)
					self.parse(htmlpage, header, dropdown)
					time.sleep(0.3)
					counter += 1

	def parse(self, htmlpage, header, dropdown):
		htmltext = htmlpage.text
		htmlurl  = htmlpage.url
		print(htmlurl)
		
		try:
			self.checkEmpty(htmltext, header, dropdown)
		except lotteryError as e:
			print("Lottery empty")

	def checkEmpty(self, htmltext, header, dropdown):
		# SuperLotto638Control_history1_Label1
		# Lotto649Control_history_Label1
		# D539Control_history1_Label1
		# Lotto1224Control_history_Label1
		# L3DControl_history1_Label1
		# L4DControl_history1_Label1
		# M638Control_history1_Label1
		# M649Control_history1_Label1
		# M539Control_history1_Label1

		soup = BeautifulSoup(htmltext, "html.parser")

		tag = soup.find("span", {"id": "{}Control_history{}_Label1".format(header, main.lottery_control[header])})
		tag2 = soup.find("input", {"id": "{}Control_history{}_txtNO".format(header, main.lottery_control[header])})
		print(tag)
		print(tag2)
		# print("查無資料" in tag)

if __name__ == "__main__":
	m = main()
	m.craw()
