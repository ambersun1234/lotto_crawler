from .lotteryBase import lotteryBase

class Lotto1224Parser(lotteryBase):
	def __init__(self, control):
		self.numbers = 12
		self.id_f = "{}No".format(super().getIDF(control))
		self.id_l = "_0"

	def parse(self, soup):
		numberList = list()

		for i in range(1, self.numbers + 1):
			number = soup.find("span", {"id": "{}{}{}".format(self.id_f, i, self.id_l)})
			numberList.append(number.text.replace("\n", ""))

		return numberList
