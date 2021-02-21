import os
import time
import sys
import requests
from bs4 import BeautifulSoup
import datetime
import re

from customException.customException import lotteryEmptyError, lotteryValidationFailed
from customException.customException import lotteryPageError
from customException.customException import serverError

from lotteryConstant.lotteryConstant import lotteryConstant

class main:
	def __init__(self):
		self.url_f      = "https://www.taiwanlottery.com.tw/"
		self.url_l      = "/history.aspx"
		self.useragent  = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
		}
		self.start_year = 103
		self.end_year   = datetime.datetime.now().year

		self.myrequests = requests.Session()

		self.viewstate          = None 
		self.viewstategenerator = None 
		self.eventvalidation    = None

	def testWrite(self, filename, content):
		with open(filename, "w") as f:
			f.write(content)
			f.close()

	def getArgs(self, element):
		htmlpage = self.myrequests.get("{}{}{}".format(self.url_f, element, self.url_l))
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		self.viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
		self.viewstate          = soup.find("input", {"id": "__VIEWSTATE"})["value"]
		self.eventvalidation    = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

		if self.viewstate is None or \
			self.viewstategenerator is None or \
			self.eventvalidation is None:
			raise lotteryValidationFailed

	def craw(self):
		# 取得 validation
		self.getArgs(lotteryConstant.lottery_type[0])
		for dropdown, header, element in zip(lotteryConstant.lottery_dropdown, lotteryConstant.lottery_header, lotteryConstant.lottery_type):
			for year in range(self.start_year, self.end_year + 1):
				counter = 1
				while True:
					tcounter = str(counter)
					prefixs = "{}Control_history1".format(header)
					myparams = {
						"__EVENTTARGET": "",
						"__EVENTARGUMENT": "",
						"__LASTFOCUS": "",
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

					echostr = "{} {}000{}".format(header, year, tcounter.zfill(3))

					if htmlpage.status_code != 200: raise serverError(htmlpage.status_code)

					self.parse(htmlpage, header, dropdown, echostr)
					time.sleep(0.1)
					counter += 1
					# 更新 validation
					self.getArgs(element)

	def echoLog(self, echostr, msgstr):
		print("{}: {}".format(echostr, msgstr))

	def parse(self, htmlpage, header, dropdown, echostr):
		msgstr = None
		try:
			self.checkServerStatus(htmlpage)
			self.checkEmpty(htmlpage, header, dropdown)
		except (lotteryEmptyError, serverError) as e:
			msgstr = e
		else:
			msgstr = htmlpage.status_code
		finally:
			self.echoLog(echostr, msgstr)

	def checkServerStatus(self, htmlpage):
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

	def checkEmpty(self, htmlpage, header, dropdown):
		htmlpage.encoding = "utf-8"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		tag = soup.find("span", {"id": "{}Control_history{}_Label1".format(header, lotteryConstant.lottery_control[header])})
		if tag is None or "查無資料" in tag: raise lotteryEmptyError

if __name__ == "__main__":
	m = main()
	m.craw()
