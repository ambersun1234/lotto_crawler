from .lotteryBase import lotteryBase

class L4DParser(lotteryBase):
	def __init__(self, control):
		self.numbers = 4
		self.id = "font_black14b_center"

	def parse(self, soup):
		numberList = list()

		number = soup.select("span", {self.id: ""})
		for i in number:
			if i.get(self.id) is not None:
				numberList.append(i.contents[0])

		return numberList
