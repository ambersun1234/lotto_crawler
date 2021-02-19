import os
import time
import sys
import requests
from bs4 import BeautifulSoup
import datetime
import re

from customException.customException import lotteryEmptyError, lotteryValidationFailed, serverError

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
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
			"Content-Type": "application/x-www-form-urlencoded"
		}
		self.start_year = 103
		self.end_year   = datetime.datetime.now().year

		self.myrequests = requests.Session()

		self.viewstate          = None 
		self.viewstategenerator = None 
		self.eventvalidation    = None

	def getArgs(self):
		htmlpage = self.myrequests.get("{}{}{}".format(self.url_f, main.lottery_type[0], self.url_l))
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		self.viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
		self.viewstate          = soup.find("input", {"id": "__VIEWSTATE"})["value"]
		self.eventvalidation    = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

		if self.viewstate is None or self.viewstategenerator is None or self.eventvalidation is None:
			raise lotteryValidationFailed

	def craw(self):
		for dropdown, header, element in zip(main.lottery_dropdown, main.lottery_header, main.lottery_type):
			for year in range(self.start_year, self.end_year + 1):
				counter = 105
				while True:
					tcounter = str(counter)
					prefixs = "{}Control_history1".format(header)
					myparams = {
						"__EVENTTARGET": "",
						"__EVENTARGUMENT": "",
						"__EVENTVALIDATION": self.eventvalidation,
						"__LASTFOCUS": "",
						"__VIEWSTATE": self.viewstate,
						"__VIEWSTATEGENERATOR": self.viewstategenerator,
						"{}$DropDownList1".format(prefixs): str(dropdown),
						"{}$chk".format(prefixs): "radNO",
						"{}$txtNo".format(prefixs): "{}000{}".format(year, tcounter.zfill(3)),
						"{}$btnSubmit".format(prefixs): "查詢",
					}
					myurl = "{}{}{}".format(self.url_f, element, self.url_l)
					htmlpage = self.myrequests.post(myurl, headers=self.useragent, data=myparams)
					print(htmlpage.status_code)
					if htmlpage.status_code != 200: raise serverError(htmlpage.status_code)

					htmltext = htmlpage.text
		
					self.parse(htmltext, header, dropdown)
					time.sleep(0.3)
					counter += 1
					sys.exit(1)

	def parse(self, htmltext, header, dropdown):
		try:
			self.checkServerStatus(htmltext)
			self.checkEmpty(htmltext, header, dropdown)
		except lotteryEmptyError as e:
			print("Lottery empty: {}".format(e))
		except serverError as e:
			print("Server error: {}".format(e))

	def checkServerStatus(self, htmltext):
		soup = BeautifulSoup(htmltext, "html.parser")
		soup.encoding = "utf-8"

		errorType = [301, 302, 400, 401, 403, 404, 500, 502, 503, 504]

		for error in errorType:
			tmp = "伺服器錯誤" in htmltext
			tmp2 = soup.body.findAll(text=re.compile(str(error)))
			if tmp is True and tmp2 is not None: raise serverError(error)

	def checkEmpty(self, htmltext, header, dropdown):
		soup = BeautifulSoup(htmltext, "html.parser")

		tag = soup.find("span", {"id": "{}Control_history{}_Label1".format(header, main.lottery_control[header])})
		print(tag)

if __name__ == "__main__":
	m = main()
	m.getArgs()
	m.craw()
