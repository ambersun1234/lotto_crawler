import os
import time
import sys
import requests
from bs4 import BeautifulSoup
import datetime

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
	lottery_dropdown = [
		1, 2, 3,
		4, 6, 7,
		8, 9, 10
	]

	def __init__(self):
		self.url_f = "https://taiwanlottery.com.tw/"
		self.url_l = "/history.aspx"
		self.start_year = 103
		self.end_year = datetime.datetime.now().year

	def craw(self):
		for dropdown, header, element in zip(main.lottery_dropdown, main.lottery_header, main.lottery_type):
			for year in range(self.start_year, self.end_year + 1):
				counter = 1
				while True:
					tcounter = str(counter)
					prefixs = "{}Control_history1".format(header)
					myparams = {
						"{}$DropDownList1".format(prefixs): int(dropdown),
						"{}$chk".format(prefixs): "radNO",
						"{}$txtNo".format(prefixs): "{}000{}".format(year, tcounter.zfill(3)),
						"{}$btnSubmit".format(prefixs): "查詢"
					}
					myurl = "{}{}{}".format(self.url_f, element, self.url_l)
					htmlpage = requests.post(myurl, params=myparams)
					print(htmlpage.url)
					counter += 1
					if "查無資料" in htmlpage.text: break

if __name__ == "__main__":
	m = main()
	m.craw()
