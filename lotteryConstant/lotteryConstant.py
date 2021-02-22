import sys
sys.path.append("..")

from lotteryParser import SuperLotto638Parser
from lotteryParser import Lotto649Parser
from lotteryParser import D539Parser

class lotteryConstant:
	# 威力彩, 大樂透, 今彩539,
	# 雙贏彩, 三星彩, 四星彩,
	# 38樂合彩, 49樂合彩, 39樂合彩
	lottery_type = [
		"lotto/superlotto638", "lotto/Lotto649", "lotto/DailyCash", 
		"Lotto1224", "Lotto/3D", "Lotto/4D", 
		"lotto/38M6", "Lotto/49M6", "Lotto/39M5"
	]
	lottery_header = [
		"SuperLotto638", "Lotto649", "D539",
		"Lotto1224", "L3D", "L4D",
		"M638", "M649", "M539"
	]
	lottery_dropdown = [
		1, 2, 5,
		4, 6, 7,
		8, 9, 10
	]
	lottery_control = {
		"SuperLotto638": "1", "Lotto649": "", "D539": "1",
		"Lotto1224" : "", "L3D": "1", "L4D": "1",
		"M638": "1", "M649": "1", "M539": "1"
	}
	lottery_parser = {
		"SuperLotto638": SuperLotto638Parser.SuperLotto638Parser(lottery_control["SuperLotto638"]),
		"Lotto649": Lotto649Parser.Lotto649Parser(lottery_control["Lotto649"])
		"D539": D539Parser.D539Parser(lottery_control["D539"])
	}
