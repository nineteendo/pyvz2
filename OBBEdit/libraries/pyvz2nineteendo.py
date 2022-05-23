from os.path import realpath
from traceback import format_exc
class LogError:
	def __init__(self, fail):
		self.fail = fail
	def error_message(self, string):
	# Print & log error
		string += "\n" + format_exc()
		self.fail.write(string + "\n")
		self.fail.flush()
		print("\033[91m" + string + "\033[0m")
	def warning_message(self, string):
	# Print & log warning
		self.fail.write("\t" + string + "\n")
		self.fail.flush()
		print("\33[93m" + string + "\33[0m")
	def input_level(self, text, minimum, maximum, preset):
	# Set input level for conversion
		try:
			if preset < minimum:
				return max(minimum, min(maximum, int(bold_input(text + " (" + str(minimum) + "-" + str(maximum) + ")"))))
			elif preset > minimum:
				print("\033[1m"+ text + "\033[0m: " + repr(preset))
			return preset
		except Exception as e:
			self.error_message(type(e).__name__ + " : " + str(e))
			self.warning_message("Defaulting to " + str(minimum))
			return minimum
def blue_print(text):
# Print in blue text
	print("\033[94m"+ text + "\033[0m")
def green_print(text):
# Print in green text
	print("\033[32m"+ text + "\033[0m")
def bold_input(text):
# Input in bold text
	return input("\033[1m"+ text + "\033[0m: ")
def path_input(text, preset):
# Input hybrid path
	if preset != "":
		print("\033[1m"+ text + "\033[0m: " + preset)
		return preset
	else:
		string = ""
		newstring = bold_input(text)
		while newstring or string == "":
			string = ""
			quoted = 0
			escaped = False
			temp_string = ""
			confirm = False
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += temp_string + char
						confirm = True
					else:
						string += temp_string + "\\" + char
					temp_string = ""
					escaped = False
				elif char == "\\":
					escaped = True
				elif quoted != 2 and char == "'":
					quoted = 1 - quoted
				elif quoted != 1 and char == '"':
					quoted = 2 - quoted
				elif quoted != 0 or char != " ":
					string += temp_string + char
					temp_string = ""
				else:
					temp_string += " "
			if string == "":
				newstring = bold_input("\033[91mEnter a path")
			else:
				newstring = ""
				string = realpath(string)
				if confirm:
					newstring = bold_input("Confirm \033[100m" + string)
		return string
def list_levels(levels):
	blue_print("""
""" +  " ".join([repr(i) + "-" + levels[i] for i in range(len(levels))]))