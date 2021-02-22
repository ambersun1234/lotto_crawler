import os
import time
import sys
import csv
import requests
from bs4 import BeautifulSoup
import datetime
import re

from customException.customException import lotteryEmptyError, lotteryValidationFailed
from customException.customException import lotteryPageError
from customException.customException import serverError

from customException.customException import stepBackNotification, breakNotification, sessionClearNotification

from lotteryConstant.lotteryConstant import lotteryConstant

class main:
	def __init__(self):
		self.url_f      = "https://www.taiwanlottery.com.tw/"
		self.url_l      = "/history.aspx"
		self.useragent  = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
		}
		self.start_year = 103
		self.end_year   = int(datetime.datetime.now().year) - 1911
		self.dirName = "./history"

		self.myrequests = requests.Session()

		self.viewstate          = None 
		self.viewstategenerator = None 
		self.eventvalidation    = None

	def testWrite(self, filename, content):
		with open(filename, "w") as f:
			f.write(content)
			f.close()

	def writeData(self, writer, data):
		writer.writerow(data)
		print(": done")

	def constructDir(self):
		if not os.path.exists(self.dirName): os.mkdir(self.dirName)

	def getArgs(self, element):
		self.myrequests.cookies.clear()
		htmlpage = self.myrequests.get("{}{}{}".format(self.url_f, element, self.url_l))
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")
		
		try:
			self.viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
			self.viewstate          = soup.find("input", {"id": "__VIEWSTATE"})["value"]
			self.eventvalidation    = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

			if self.viewstate is None or \
				self.viewstategenerator is None or \
				self.eventvalidation is None:
				raise lotteryValidationFailed
		except (TypeError, lotteryValidationFailed) as e:
			print(e)

	def craw(self):
		self.constructDir()
		# 連續伺服器錯誤紀錄
		previous_fault = False
		current_fault = False
		fault_count = 0

		for dropdown, header, element in zip(lotteryConstant.lottery_dropdown, lotteryConstant.lottery_header, lotteryConstant.lottery_type):
			# 取得 validation
			self.getArgs(element)
			self.start_year = 103

			with open("{}/{}.csv".format(self.dirName, header), "w") as f:
				writer = csv.writer(f)

				for year in range(self.start_year, self.end_year + 1):
					counter = 1
					while True:
						tcounter = str(counter)
						prefixs = "{}Control_history{}".format(header, lotteryConstant.lottery_control[header])
						myparams = {
							"__EVENTTARGET": "",
							"__EVENTARGUMENT": "",
							"__LASTFOCUS": "",
							"__VIEWSTATEENCRYPTED": "",
							"__VIEWSTATE": self.viewstate,
							"__VIEWSTATEGENERATOR": self.viewstategenerator,
							"__EVENTVALIDATION": self.eventvalidation,
							"{}$DropDownList1".format(prefixs): "{}".format(dropdown),
							"{}$chk".format(prefixs): "radNO",
							"{}$txtNO".format(prefixs): "{}000{}".format(year, tcounter.zfill(3)),
							"{}$btnSubmit".format(prefixs): "查詢",
						}
						myurl = "{}{}{}".format(self.url_f, element, self.url_l)
						htmlpage = self.myrequests.post(myurl, headers=self.useragent, data=myparams)

						serialNumber = myparams["{}$txtNO".format(prefixs)]

						try:
							if fault_count >= 10: raise sessionClearNotification

							data = self.parse(htmlpage, header, dropdown, "{} {}".format(header, serialNumber))
							data.insert(0, serialNumber)
							print(data, end='')

							self.writeData(writer, data)
						except stepBackNotification as e:
							current_fault = True
							counter -= 1
						except breakNotification as e:
							break
						except sessionClearNotification as e:
							self.getArgs(element)
						finally:
							fault_count += 1 if previous_fault and current_fault is True else 0
							# propagation
							previous_fault = current_fault
							current_fault = False

						time.sleep(0.1)
						counter += 1
				f.close()
			time.sleep(10)

	def echoLog(self, echostr, msgstr):
		print("{}: {}".format(echostr, msgstr))

	def parse(self, htmlpage, header, dropdown, echostr):
		msgstr = htmlpage.status_code
		numbers = list()
		flag = None

		try:
			self.checkServerStatus(htmlpage)
			self.checkEmpty(htmlpage, header)
			numbers = self.parseNumber(htmlpage, header)
		except lotteryEmptyError as e:
			msgstr = e
			flag = 1
		except serverError as e:
			msgstr = e
			flag = 2
		finally:
			self.echoLog(echostr, msgstr)
			if flag == 1: raise breakNotification
			if flag == 2: raise stepBackNotification

			return numbers

	def parseNumber(self, htmlpage, header):
		htmlpage.encoding = "utf-8"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		numbers = lotteryConstant.lottery_parser[header].parse(soup)
		return numbers
		
	def checkServerStatus(self, htmlpage):
		if htmlpage.status_code != 200: raise serverError(htmlpage.status_code)

		# htmlpage.encoding = "ISO-8859-1"
		htmlpage.encoding = "big5"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		tmp = "伺服器錯誤" in htmltext
		if tmp is None: return

		errorType = [301, 302, 400, 401, 403, 404, 500, 502, 503, 504]
		for error in errorType:
			tmp2 = soup.body.findAll(text=re.compile(str(error)))
			if tmp is True and tmp2 is not None: raise serverError(error)

	def checkEmpty(self, htmlpage, header):
		htmlpage.encoding = "utf-8"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		tag = soup.find("span", {"id": "{}Control_history{}_Label1".format(header, lotteryConstant.lottery_control[header])})
		if tag is None or "查無資料" in tag: raise lotteryEmptyError

if __name__ == "__main__":
	m = main()
	m.craw()
