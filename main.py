import os
import time
import sys
import csv
import requests
from bs4 import BeautifulSoup
import datetime
import re

from customException.customException import LotteryEmptyError, LotteryValidationFailed
from customException.customException import LotteryPageError
from customException.customException import ServerError

from customException.customException import StepBackNotification, BreakNotification, SessionClearNotification

from lotteryConstant.lotteryConstant import lottery_constant

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

		self.session_requests = requests.Session()

		self.viewstate          = None 
		self.viewstategenerator = None 
		self.eventvalidation    = None

	def test_write(self, filename, content):
		with open(filename, "w") as f:
			f.write(content)
			f.close()

	def write_data(self, writer, data):
		writer.writerow(data)
		print(": done")

	def construct_dir(self):
		if not os.path.exists(self.dirName): os.mkdir(self.dirName)

	def get_args(self, element):
		self.session_requests.cookies.clear()
		htmlpage = self.session_requests.get("{}{}{}".format(self.url_f, element, self.url_l))
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")
		
		try:
			self.viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
			self.viewstate          = soup.find("input", {"id": "__VIEWSTATE"})["value"]
			self.eventvalidation    = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

			if self.viewstate is None or \
				self.viewstategenerator is None or \
				self.eventvalidation is None:
				raise LotteryValidationFailed
		except (TypeError, LotteryValidationFailed) as e:
			print(e)

	def craw(self):
		self.construct_dir()
		# 連續伺服器錯誤紀錄
		previous_fault = False
		current_fault = False
		fault_count = 0

		for dropdown, header, element in zip(lottery_constant.lottery_dropdown, lottery_constant.lottery_header, lottery_constant.lottery_type):
			# 取得 validation
			self.get_args(element)
			self.start_year = 103

			with open("{}/{}.csv".format(self.dirName, header), "w") as f:
				writer = csv.writer(f)

				for year in range(self.start_year, self.end_year + 1):
					counter = 1
					while True:
						inner_counter = str(counter)
						prefix = "{}Control_history{}".format(header, lottery_constant.lottery_control[header])
						query_params = {
							"__EVENTTARGET": "",
							"__EVENTARGUMENT": "",
							"__LASTFOCUS": "",
							"__VIEWSTATEENCRYPTED": "",
							"__VIEWSTATE": self.viewstate,
							"__VIEWSTATEGENERATOR": self.viewstategenerator,
							"__EVENTVALIDATION": self.eventvalidation,
							"{}$DropDownList1".format(prefix): "{}".format(dropdown),
							"{}$chk".format(prefix): "radNO",
							"{}$txtNO".format(prefix): "{}000{}".format(year, inner_counter.zfill(3)),
							"{}$btnSubmit".format(prefix): "查詢",
						}
						query_url = "{}{}{}".format(self.url_f, element, self.url_l)
						htmlpage = self.session_requests.post(query_url, headers=self.useragent, data=query_params)

						serialNumber = query_params["{}$txtNO".format(prefix)]

						try:
							if fault_count >= 10: raise SessionClearNotification

							data = self.parse(htmlpage, header, dropdown, "{} {}".format(header, serialNumber))
							data.insert(0, serialNumber)
							print(data, end='')

							self.write_data(writer, data)
						except StepBackNotification as e:
							current_fault = True
							counter -= 1
						except BreakNotification as e:
							break
						except SessionClearNotification as e:
							self.get_args(element)
						finally:
							fault_count += 1 if previous_fault and current_fault is True else 0
							# propagation
							previous_fault = current_fault
							current_fault = False

						time.sleep(0.1)
						counter += 1
				f.close()
			time.sleep(10)

	def echo_log(self, echostr, msgstr):
		print("{}: {}".format(echostr, msgstr))

	def parse(self, htmlpage, header, dropdown, echostr):
		msgstr = htmlpage.status_code
		numbers = list()
		flag = None

		try:
			self.check_server_status(htmlpage)
			self.check_empty(htmlpage, header)
			numbers = self.parse_number(htmlpage, header)
		except LotteryEmptyError as e:
			msgstr = e
			flag = 1
		except ServerError as e:
			msgstr = e
			flag = 2
		finally:
			self.echo_log(echostr, msgstr)
			if flag == 1: raise BreakNotification
			if flag == 2: raise StepBackNotification

			return numbers

	def parse_number(self, htmlpage, header):
		htmlpage.encoding = "utf-8"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		numbers = lottery_constant.lottery_parser[header].parse(soup)
		return numbers
		
	def check_server_status(self, htmlpage):
		if htmlpage.status_code != 200: raise ServerError(htmlpage.status_code)

		# htmlpage.encoding = "ISO-8859-1"
		htmlpage.encoding = "big5"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		tmp = "伺服器錯誤" in htmltext
		if tmp is None: return

		errorType = [301, 302, 400, 401, 403, 404, 500, 502, 503, 504]
		for error in errorType:
			tmp2 = soup.body.findAll(text=re.compile(str(error)))
			if tmp is True and tmp2 is not None: raise ServerError(error)

	def check_empty(self, htmlpage, header):
		htmlpage.encoding = "utf-8"
		htmltext = htmlpage.text
		soup = BeautifulSoup(htmltext, "html.parser")

		tag = soup.find("span", {"id": "{}Control_history{}_Label1".format(header, lottery_constant.lottery_control[header])})
		if tag is None or "查無資料" in tag: raise LotteryEmptyError

if __name__ == "__main__":
	m = main()
	m.craw()
