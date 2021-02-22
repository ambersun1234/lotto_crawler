from .lotteryBase import lotteryBase

class L3DParser(lotteryBase):
	def __init__(self, control):
		self.numbers = 3
		self.id = "font_black14b_center"

	def parse(self, soup):
		numberList = list()

		number = soup.select("span[class*=\"{}\"]".format(self.id))
		for i in number:
			numberList.append(i.contents[0])

		return numberList
