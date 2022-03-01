class LotteryEmptyError(Exception):
	def __init__(self):
		super().__init__("no data found")

class LotteryPageError(Exception):
	def __init__(self):
		super().__init__("error getting page")

class LotteryValidationFailed(Exception):
	def __init__(self):
		super().__init__("cannot get validation argument")

class ServerError(Exception):
	def __init__(self, code):
		super().__init__("HTTP status code: {}".format(code))

class SessionClearNotification(Exception):
	def __init__(self):
		super().__init__()

class StepBackNotification(Exception):
	def __init__(self):
		super().__init__()

class BreakNotification(Exception):
	def __init__(self):
		super().__init__()
