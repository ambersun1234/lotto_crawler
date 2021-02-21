class lotteryBase(object):
	def __init__(self):
		pass

	def parse(self, soup):
		raise NotImplementedError

	def getLotteryName(self):
		return type(self).__qualname__.replace("Parser", "")

	def getIDF(self, control):
		return "{}Control_history{}_dlQuery_".format(self.getLotteryName(), control)
