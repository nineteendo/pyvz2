# Import libraries
import sys, datetime
from traceback import format_exc
from json import load
from struct import pack, unpack
from os import makedirs, listdir, system, getcwd
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext

# Default Options
options = {
	"binObjClasses": (
		"drapersavedata",
		"globalsavedata",
		"playerinfolocalsavedata",
		"lootsavedata",
		"savegameheader"
	),
	"cachLimit": 1048575,
	"comma": 0,
	"confirmPath": True,
	"datObjClasses": (
		"playerinfo",
	),
	"DEBUG_MODE": True,
	"doublepoint": 1,
	"enteredPath": False,
	"indent": -1,
	"RTONExtensions": (
		".bin",
		".dat",
		".rton",
		".section"
	),
	"RTONNoExtensions": (
		"draper_",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"repairFiles": False,
	"shortNames": False,
	"sortKeys": False,
	"sortValues": False
}

# Print & log error
def error_message(string):
	if DEBUG_MODE:
		string += "\n" + format_exc()
	
	fail.write(string + "\n")
	fail.flush()
	print("\033[91m%s\033[0m" % string)

# Print in blue text
def blue_print(text):
	print("\033[94m%s\033[0m" % text)

# Print in green text
def green_print(text):
	print("\033[32m%s\033[0m" % text)

# Input in bold text
def bold_input(text):
	return input("\033[1m%s\033[0m: " % text)

# Input hybrid path
def path_input(text):
	string = ""
	newstring = bold_input(text)
	while newstring or string == "":
		if options["enteredPath"]:
			string = newstring
		else:
			string = ""
			quoted = 0
			escaped = False
			tempstring = ""
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += tempstring + char
					else:
						string += tempstring + "\\" + char
					
					tempstring = ""
					escaped = False
				elif char == "\\":
					escaped = True
				elif quoted != 2 and char == "'":
					quoted = 1 - quoted
				elif quoted != 1 and char == '"':
					quoted = 2 - quoted
				elif quoted != 0 or char != " ":
					string += tempstring + char
					tempstring = ""
				else:
					tempstring += " "

		if string == "":
			newstring = bold_input("\033[91mEnter a path")
		else:
			newstring = ""
			string = realpath(string)
			if options["confirmPath"]:
				newstring = bold_input("Confirm \033[100m" + string)

	return string

# Extra list class
class list2:
	def __init__(self, data):
		self.data = data

# Inf and -inf values
Infinity = [float("Infinity"), float("-Infinity")]

# Boolian
def encode_bool(boolean):
	if boolean == False:
		return b"\x00"
	else:
		return b"\x01"

# Number with variable length
def encode_number(integ):
	integ, i = divmod(integ, 128)
	if (integ):
		i += 128
	
	string = pack("B", i)
	while integ:
		integ, i = divmod(integ, 128)
		if (integ):
			i += 128
		
		string += pack("B", i)
	
	return string

# Unicode string
def encode_unicode(string):
	encoded_string = string.encode()
	return encode_number(len(string)) + encode_number(len(encoded_string)) + encoded_string

# RTID
def encode_rtid(string):
	if "@" in string:
		name, type = string[5:-1].split("@")
		if name.count(".") == 2:
			i2, i1, i3 = name.split(".")
			return b"\x83\x02" + encode_unicode(type) + encode_number(int(i1)) + encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
		else:
			return b"\x83\x03" + encode_unicode(type) + encode_unicode(name)
	else:
		return b"\x83\x00"

# Number
def encode_int(integ):
	if integ == 0:
		return b"\x21"
	elif -128 <= integ <= 127:
		return b"\x08" + pack("b", integ)
	elif 0 <= integ <= 255:
		return b"\x0a" + pack("B", integ)
	elif -32768 <= integ <= 32767:
		return b"\x10" + pack("<h", integ)
	elif 0 <= integ < 65535:
		return b"\x12" + pack("<H", integ)
	elif 0 <= integ <= 2097151:
		return b"\x24" + encode_number(integ)
	elif -2097151 <= integ <= 0:
		return b"\x25" + encode_number(-integ)
	elif -2147483648 <= integ <= 2147483647:
		return b"\x20" + pack("<i", integ)
	elif 0 <= integ < 4294967295:
		return b"\x26" + pack("<I", integ)
	elif 0 <= integ <= 562949953421311:
		return b"\x44" + encode_number(integ)
	elif -562949953421311 <= integ <= 0:
		return b"\x45" + encode_number(-integ)
	elif -9223372036854775808 <= integ <= 9223372036854775807:
		return b"\x40" + pack("<q", integ)
	elif 0 <= integ <= 18446744073709551615:
		return b"\x46" + pack("<Q", integ)
	elif 0 <= integ:
		return b"\x44" + encode_number(integ)
	else:
		return b"\x45" + encode_number(-integ)

# Float
def encode_float(dec):
	if dec == 0:
		return b"\x23"
	elif dec != dec or dec in Infinity or -340282346638528859811704183484516925440 <= dec <= 340282346638528859811704183484516925440 and dec == unpack("<f", pack("<f", dec))[0]:
		return b"\x22" + pack("<f", dec)
	else:
		return b"\x42" + pack("<d", dec)

# String
def encode_string(string, cached_strings, cached_printable_strings):
	if len(string) == len(string.encode("latin-1", "ignore")):
		if string in cached_strings:
			data = b"\x91" + encode_number(cached_strings[string])
		elif len(cached_strings) < cachLimit:
			cached_strings[string] = len(cached_strings)
			data = b"\x90" + encode_number(len(string)) + string.encode("latin-1")
		else:
			data = b"\x81" + encode_number(len(string)) + string.encode("latin-1")
	else:
		if string in cached_printable_strings:
			data = b"\x93" + encode_number(cached_printable_strings[string])
		elif len(cached_printable_strings) < cachLimit:
			cached_printable_strings[string] = len(cached_printable_strings)
			data = b"\x92" + encode_unicode(string)
		else:
			data = b"\x82" + encode_unicode(string)
	
	return (data, cached_strings, cached_printable_strings)

# Array
def parse_array(data, cached_strings, cached_printable_strings):
	string = encode_number(len(data))
	for v in data:
		v, cached_strings, cached_printable_strings = parse_data(v, cached_strings, cached_printable_strings)
		string += v
	
	return (b"\x86\xfd" + string + b"\xfe", cached_strings, cached_printable_strings)

# Object
def parse_object(data, cached_strings, cached_printable_strings):
	string = b"\x85"
	for key, value in data:
		key, cached_strings, cached_printable_strings = encode_string(key, cached_strings, cached_printable_strings)
		value, cached_strings, cached_printable_strings = parse_data(value, cached_strings, cached_printable_strings)
		string += key + value
	
	return (string + b"\xff", cached_strings, cached_printable_strings)

# JSON -> RTON
def parse_json(data):
	cached_strings = {}
	cached_printable_strings = {}
	string = b"RTON\x01\x00\x00\x00"
	for key, value in data:
		key, cached_strings, cached_printable_strings = encode_string(key, cached_strings, cached_printable_strings)
		value, cached_strings, cached_printable_strings = parse_data(value, cached_strings, cached_printable_strings)
		string += key + value
	
	return string + b"\xffDONE"

# Data
def parse_data(data, cached_strings, cached_printable_strings):
	if isinstance(data, list):
		return parse_array(data, cached_strings, cached_printable_strings)
	elif isinstance(data, list2):
		return parse_object(data.data, cached_strings, cached_printable_strings)
	elif isinstance(data, bool):
		return (encode_bool(data), cached_strings, cached_printable_strings)
	elif isinstance(data, int):
		return (encode_int(data), cached_strings, cached_printable_strings)
	elif isinstance(data, float):
		return (encode_float(data), cached_strings, cached_printable_strings)
	elif isinstance(data, str):
		if data.startswith("RTID(") and data.startswith(")"):
			return (encode_rtid(data), cached_strings, cached_printable_strings)
		else:
			return encode_string(data, cached_strings, cached_printable_strings)
	else:
		raise TypeError(type(data))

# Convert file
def conversion(inp, out, pathout):
	if isdir(inp) and inp != pathout:
		makedirs(out, exist_ok = True)
		for entry in sorted(listdir(inp)):
			conversion(osjoin(inp, entry), osjoin(out, entry), pathout)
	elif isfile(inp) and inp.lower().endswith(".json"):
		write = out.removesuffix(".json")
		try:
			data = load(open(inp, "rb"), object_pairs_hook = encode_object_pairs).data
		except Exception as e:
			error_message("%s in %s: %s" % (type(e).__name__, inp, e))
		else:
			try:
				encoded_data = parse_json(data)
				# No RTON extension
				if "" == splitext(write)[1] and not basename(write).lower().startswith(RTONNoExtensions):
					vals = list(values_from_keys(data, ["objects","objclass"]))
					if any(value in vals for value in datObjClasses):
						write += ".dat"
					elif any(value in vals for value in binObjClasses):
						write += ".bin"
					else:
						write += ".rton"
				
				open(write, "wb").write(encoded_data)
				print("wrote " + relpath(write, pathout))
			except Exception as e:
				error_message("%s in %s: %s" % (type(e).__name__, inp, e))

# Object to list of tuples
def encode_object_pairs(pairs):
	return list2(pairs)

# Search in json file
def values_from_keys(data, keyz):
	if keyz == []:
		yield str(data).lower()
	elif isinstance(data, list):
		for val in data:
			yield from values_from_keys(val, keyz)
	elif isinstance(data, list2):
		for val in data.data:
			yield from values_from_keys(val, keyz)
	elif isinstance(data, tuple):
		key, value = data
		if keyz[0] == key:
			yield from values_from_keys(value, keyz[1:])

# Start of the code
try:
	system("")
	if getattr(sys, "frozen", False):
		application_path = dirname(sys.executable)
	else:
		application_path = sys.path[0]

	fail = open(osjoin(application_path, "fail.txt"), "w")
	if sys.version_info[:2] < (3, 9):
		raise RuntimeError("Must be using Python 3.9")
	
	print("\033[95m\033[1mJSON RTONEncoder v1.1.0\n(C) 2022 by Nineteendo\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
				elif key == "Indent" and type(newoptions[key]) in [int, type(None)]:
					options[key] = newoptions[key]
	except Exception as e:
		error_message("%s in options.json: %s" % (type(e).__name__, e))
	
	binObjClasses = options["binObjClasses"]
	cachLimit = options["cachLimit"]
	datObjClasses = options["datObjClasses"]
	DEBUG_MODE = options["DEBUG_MODE"]
	RTONNoExtensions = options["RTONNoExtensions"]
	blue_print("Working directory: " + getcwd())
	pathin = path_input("Input file or directory")
	if isfile(pathin):
		pathout = path_input("Output file").removesuffix(".json")
	else:
		pathout = path_input("Output directory")
	
	# Start conversion
	start_time = datetime.datetime.now()
	conversion(pathin, pathout, dirname(pathout))
	green_print("finished converting %s in %s" % (pathin, datetime.datetime.now() - start_time))
	bold_input("\033[95mPRESS [ENTER]")
except BaseException as e:
	error_message("%s: %s" % (type(e).__name__, e))

# Close log
fail.close()