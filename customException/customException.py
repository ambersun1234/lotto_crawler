class lotteryEmptyError(Exception):
	def __init__(self):
		super().__init__("lottery empty: no data found")

class serverError(Exception):
	def __init__(self, code):
		super().__init__("HTTP status code: {}".format(code))

class lotteryValidationFailed(Exception):
	def __init__(self):
		super().__init__("lottery validation failed: cannot get validation argument")


