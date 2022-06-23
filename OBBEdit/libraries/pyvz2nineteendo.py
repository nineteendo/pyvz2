import datetime
from io import StringIO
from json import load
from os import listdir, system
from os.path import dirname, isfile, join as osjoin, realpath, splitext
import sys
from traceback import format_exc
def initialize():
	system("")
	if getattr(sys, "frozen", False):
		return dirname(sys.executable)
	else:
		return sys.path[0]
class LogError:
	def __init__(self, fail):
		try:
			self.fail = open(fail, "w")
		except PermissionError as e:
			self.fail = StringIO()
			self.fail.name = None
			self.error_message(e)
	def error_message(self, e, sub = "", string = ""):
	# Print & log error
		string += type(e).__name__ + sub + ": " + str(e) + "\n" + format_exc()
		self.fail.write(string + "\n")
		self.fail.flush()
		print("\033[91m" + string + "\033[0m")
	def warning_message(self, string):
	# Print & log warning
		self.fail.write("\t" + string + "\n")
		self.fail.flush()
		print("\33[93m" + string + "\33[0m")
	
	def check_version(self, mayor = 2, minor = 0, micro = 0):
		if sys.version_info[:3] < (mayor, minor, micro):
			raise BaseException("Must be using Python " + repr(mayor) + "." + repr(minor) + "." + repr(micro) + " or newer")
	def input_level(self, text, minimum, maximum, preset):
	# Set input level for conversion
		try:
			if preset < minimum:
				return max(minimum, min(maximum, int(bold_input(text + " (" + str(minimum) + "-" + str(maximum) + ")"))))
			elif preset > minimum:
				print("\033[1m"+ text + "\033[0m: " + repr(preset))
			return preset
		except Exception as e:
			self.error_message(e)
			self.warning_message("Defaulting to " + str(minimum))
			return minimum
	def load_template(self, options, folder, index):
	# Load template into options
		try:
			templates = {}
			blue_print("\033[1mTEMPLATES:\033[0m")
			for entry in sorted(listdir(folder)):
				if isfile(osjoin(folder, entry)):
					file, extension = splitext(entry)
					if extension == ".json" and entry.count("--") == 2:
						dash_list = file.split("--")
						key = dash_list[0].lower()
						if not key in templates:
							blue_print("\033[1m" + key + "\033[0m: " + dash_list[index])
							templates[key] = entry
					elif entry.count("--") > 0:
						print("\033[1m"+ "--".join(file.split("--")[1:]) + "\033[0m")
			length = len(templates)
			if length == 0:
				green_print("Loaded default template")
			else:
				if length > 1:
					key = bold_input("Choose template").lower()
				
				name = templates[key]
				newoptions = load(open(osjoin(folder, name), "rb"))
				for key in options:
					if key in newoptions and newoptions[key] != options[key]:
						if type(options[key]) == type(newoptions[key]):
							options[key] = newoptions[key]
						elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
							options[key] = tuple([str(i).lower() for i in newoptions[key]])
						elif key == "indent" and newoptions[key] == None:
							options[key] = newoptions[key]
				green_print("Loaded template " + name)
		except Exception as e:
			self.error_message(e, "while loading options: ")
			self.warning_message("Falling back to default options.")
		return options
	def finish_program(self, message, start):
		green_print(message + " " + str(datetime.datetime.now() - start))
		if self.fail.tell() > 0:
			name = self.fail.name
			if name == None:
				open(path_input("\33[93mErrors occured, dump to\33[0m", ""), "w").write(self.fail.getvalue())
			else:
				print("\33[93mErrors occured, check: " + self.fail.name + "\33[0m")
		bold_input("\033[95mPRESS [ENTER]")
	def close(self):
	# Close fail file
		self.fail.close()
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
				processed_string = realpath(string)
				if confirm or processed_string != string:
					newstring = bold_input("Confirm \033[100m" + processed_string)
		return processed_string
def list_levels(levels):
	blue_print("""
""" +  " ".join([repr(i) + "-" + levels[i] for i in range(len(levels))]))