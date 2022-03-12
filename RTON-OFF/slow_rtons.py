# RTON parser
# written by 1Zulu and Nineteendo

# Import libraries
import sys, datetime
from traceback import format_exc
from json import load, dump
from struct import unpack, error
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
	"comma": 0,
	"confirmPath": True,
	"datObjClasses": (
		"playerinfo",
	),
	"DEBUG_MODE": False,
	"doublepoint": 1,
	"ensureAscii": False,
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
	"shortNames": True,
	"sortKeys": False,
	"sortValues": False
}

# List of tuples to fake object
class FakeDict(dict):
	def __init__(self, items):
		if items != []:
			self["something"] = "something"
		
		self._items = items
	def items(self):
		return self._items

# Print & log error
def error_message(string):
	if options["DEBUG_MODE"]:
		string += "\n" + format_exc()
	
	fail.write(string + "\n")
	fail.flush()
	print("\033[91m" + string + "\033[0m")

# Print & log warning
def warning_message(string):
	fail.write("\t" + string + "\n")
	fail.flush()
	print("\33[93m" + string + "\33[0m")

# Print in blue text
def blue_print(text):
	print("\033[94m"+ text + "\033[0m")

# Print in green text
def green_print(text):
	print("\033[32m"+ text + "\033[0m")

# Input in bold text
def bold_input(text):
	return input("\033[1m"+ text + "\033[0m: ")

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

# type 08
def parse_int8(fp):
	return unpack("b", fp.read(1))[0]

# type 0a
def parse_uint8(fp):
	return unpack("B", fp.read(1))[0]
	
# type 10
def parse_int16(fp):
	return unpack("<h", fp.read(2))[0]

# type 12
def parse_uint16(fp):
	return unpack("<H", fp.read(2))[0]
	
# type 20
def parse_int32(fp):
	return unpack("<i", fp.read(4))[0]

# type 22
def parse_float(fp):
	return unpack("<f", fp.read(4))[0]
	
# type 24, 28, 44 and 48
def parse_uvarint(fp):
	result = 0
	i = 1
	while i == 1 or num > 127:
		num = unpack("B", fp.read(1))[0]
		result += i * (num & 0x7f)
		i *= 128
	
	return result

# type 25, 29, 45 and 49
def parse_varint(fp):
	num = parse_uvarint(fp)
	if num % 2:
		num = -num -1

	return num // 2

# type 26
def parse_uint32(fp):
	return unpack("<I", fp.read(4))[0]

# type 40
def parse_int64(fp):
	return unpack("<q", fp.read(8))[0]

# type 42
def parse_double(fp):
	return unpack("<d", fp.read(8))[0]

# type 46
def parse_uint64(fp):
	return unpack("<Q", fp.read(8))[0]
	
# types 81, 90
def parse_str(fp):
	byte = fp.read(parse_uvarint(fp))
	try:
		return byte.decode("utf-8")
	except Exception:
		return byte.decode("latin-1")
	
# type 82, 92
def parse_printable_str(fp):
	i1 = parse_uvarint(fp) # Character length
	string = fp.read(parse_uvarint(fp)).decode()
	i2 = len(string)
	if i1 != i2:
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": Unicode string of character length " + str(i2) + " found, expected " + str(i1))
	
	return string
	
# types 90, 91, 92, 93
def parse_cached_str(fp, code, chached_strings, chached_printable_strings):
	if code == b"\x90":
		result = parse_str(fp)
		chached_strings.append(result)
	elif code in b"\x91":
		result = chached_strings[parse_uvarint(fp)]
	elif code in b"\x92":
		result = parse_printable_str(fp)
		chached_printable_strings.append(result)
	elif code in b"\x93":
		result = chached_printable_strings[parse_uvarint(fp)]
	
	return (result, chached_strings, chached_printable_strings)

# type 83
def parse_ref(fp):
	ch = fp.read(1)
	if ch == b"\x00":
		return "RTID()"
	elif ch == b"\x02":
		p1 = parse_printable_str(fp)
		i2 = str(parse_uvarint(fp))
		i1 = str(parse_uvarint(fp))
		return "RTID(" + i1 + "." + i2 + "." + fp.read(4)[::-1].hex() + "@" + p1 + ")"
	elif ch == b"\x03":
		p1 = parse_printable_str(fp)
		return "RTID(" + parse_printable_str(fp) + "@" + p1 + ")"
	else:
		raise ValueError("unexpected headbyte for type 83, found: " + ch.hex())

def parse_root_map(fp):
	result = []
	try:
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, [], [])
			val, chached_strings, chached_printable_strings = parse(fp, chached_strings, chached_printable_strings)
			result.append((key,val))
	except KeyError as k:
		if str(k) == 'b""':
			if options["repairFiles"]:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		else:
			raise TypeError("unknown tag " + k.args[0].hex())
	except error:
		if options["repairFiles"]:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	except StopIteration:
		pass
	
	if options["sortKeys"]:
		result = sorted(result)
	
	return FakeDict(result)

# type 85
def parse_map(fp, chached_strings, chached_printable_strings):
	result = []
	try:
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, chached_strings, chached_printable_strings)
			val, chached_strings, chached_printable_strings = parse(fp, chached_strings, chached_printable_strings)
			result.append((key,val))
	except KeyError as k:
		if str(k) == 'b""':
			if options["repairFiles"]:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		else:
			raise TypeError("unknown tag " + k.args[0].hex())
	except error:
		if options["repairFiles"]:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	except StopIteration:
		pass
	
	if options["sortKeys"]:
		result = sorted(result)
	
	return (FakeDict(result), chached_strings, chached_printable_strings)

# type 86
def parse_list(fp, chached_strings, chached_printable_strings):	
	code = fp.read(1)
	if code != b"\xfd":
		raise KeyError("List starts with " + code.hex())
	
	result = []
	i1 = 0
	i2 = parse_uvarint(fp)
	try:
		while True:
			val, chached_strings, chached_printable_strings = parse(fp, chached_strings, chached_printable_strings)
			result.append(val)
			i1 += 1
	except KeyError as k:
		if str(k) == 'b""':
			if options["repairFiles"]:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		else:
			raise TypeError("unknown tag " + k.args[0].hex())
	except error:
		if options["repairFiles"]:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	except StopIteration:
		pass
	
	if (i1 != i2):
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() -1) + ": Array of length " + str(i1) + " found, expected " + str(i2))
	
	if options["sortValues"]:
		result = sorted(result)
	
	return (result, chached_strings, chached_printable_strings)

# Stop reading list and object
def end(fp):
	raise StopIteration

# Parse data type
def parse(fp, chached_strings, chached_printable_strings):
	# mappings
	mappings = {	
		b"\x00": lambda x: False,
		b"\x01": lambda x: True,
		b"\x08": parse_int8,  
		b"\x09": lambda x: 0, # int8_zero
		b"\x0a": parse_uint8,
		b"\x0b": lambda x: 0, # uint8_zero
		b"\x10": parse_int16,
		b"\x11": lambda x: 0,  # int16_zero
		b"\x12": parse_uint16,
		b"\x13": lambda x: 0, # uint16_zero
		b"\x20": parse_int32,
		b"\x21": lambda x: 0, # int32_zero
		b"\x22": parse_float,
		b"\x23": lambda x: 0.0, # float_zero
		b"\x24": parse_uvarint, # positive_int32_varint
		b"\x25": parse_uvarint, # negative_int32_varint
		# only in NoBackup RTONs
		b"\x26": parse_uint32,
		b"\x27": lambda x: 0, #uint_32_zero
		b"\x28": parse_uvarint, # positive_uint32_varint
		b"\x29": parse_uvarint, #negative_int32_varint
		b"\x40": parse_int64,
		b"\x41": lambda x: 0, #int64_zero
		b"\x42": parse_double,
		b"\x43": lambda x: 0.0, # double_zero
		b"\x44": parse_uvarint, # positive_int64_varint
		b"\x45": parse_uvarint, # negative_int64_varint
		b"\x46": parse_uint64,
		b"\x47": lambda x: 0, # uint64_zero
		b"\x48": parse_uvarint, # positive_uint64_varint
		b"\x49": parse_uvarint, # negative_uint64_varint
		
		b"\x81": parse_str, # uncached string
		b"\x82": parse_printable_str, # uncached printable string
		b"\x83": parse_ref,
		b"\x84": lambda x: "null", # null reference
		b"\xfe": end, 
		b"\xff": end
	}
	cached_data = {
		b"\x85": parse_map,
		b"\x86": parse_list
	}
	code = fp.read(1)
	# handle string types
	if code in [b"\x90", b"\x91", b"\x92", b"\x93"]:
		return parse_cached_str(fp, code, chached_strings, chached_printable_strings)
	# handle cached strings
	elif code in cached_data:
		return cached_data[code](fp, chached_strings, chached_printable_strings)
	else:
		return (mappings[code](fp), chached_strings, chached_printable_strings)

# Recursive file convert function
def conversion(inp, out, pathout):
	if isfile(inp) and (inp.lower().endswith(options["RTONExtensions"]) or basename(inp).lower().startswith(options["RTONNoExtensions"])):	
		if options["shortNames"]:
			out = splitext(out)[0]
			 
		jfn = out + ".json"
		file = open(inp, "rb")
		try:
			if file.read(8) == b"RTON\x01\x00\x00\x00":
				data = parse_root_map(file)
				dump(data, open(jfn, "w"), ensure_ascii = ensureAscii, indent = indent, separators = separators)
				print("wrote " + relpath(jfn, pathout))
			else:
				raise Warning("No RTON")
		except Exception as e:
			error_message("%s in %s pos %s: %s" % (type(e).__name__, inp, file.tell() - 1, e))
	elif isdir(inp) and inp != pathout:
		makedirs(out, exist_ok=True)
		for entry in listdir(inp):
			conversion(osjoin(inp, entry), osjoin(out, entry), pathout)

# Start code
try:
	system("")
	if getattr(sys, "frozen", False):
		application_path = dirname(sys.executable)
	else:
		application_path = sys.path[0]

	fail = open(osjoin(application_path, "fail.txt"), "w")
	if sys.version_info[:2] < (3, 9):
		raise RuntimeError("Must be using Python 3.9")
	
	print("\033[95m\033[1mSLOW RTONParser v1.1.0\n(C) 2022 by Nineteendo\n\33[93mOnly here for compatibility reasons. DON'T USE!\33[0m\n")
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
	
	if options["comma"] > 0:
		comma = "," + " " * options["comma"]
	else:
		comma = ","

	if options["doublepoint"] > 0:
		separators = (comma, ":" + " " * options["doublepoint"])
	else:
		separators = (comma, ":")

	if options["indent"] == None:
		indent = None
	elif options["indent"] < 0:
		indent = "\t"
	else:
		indent = " " * options["indent"]
	
	ensureAscii = options["ensureAscii"]
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
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")

	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))


# Close log
fail.close()