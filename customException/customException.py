class lotteryEmptyError(Exception):
	def __init__(self):
		super().__init__("no data found")

class lotteryPageError(Exception):
	def __init__(self):
		super().__init__("error getting page")

class lotteryValidationFailed(Exception):
	def __init__(self):
		super().__init__("cannot get validation argument")

class serverError(Exception):
	def __init__(self, code):
		super().__init__("HTTP status code: {}".format(code))

class stepBackNotification(Exception):
	def __init__(self):
		super().__init__()

class breakNotification(Exception):
	def __init__(self):
		super().__init__()
