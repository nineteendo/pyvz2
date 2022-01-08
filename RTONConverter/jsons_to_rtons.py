# JSON parser
# written by Nineteendo
# usage: put json files in jsons & run

import os, json, struct, sys, traceback, datetime

# Default Options
options = {
	"AllowNan": True,
	"AllowAllJSON": True,
	"BinObjclasses": (
		"DraperSaveData",
		"GlobalSaveData",
		"PlayerInfoLocalSaveData",
		"LootSaveData",
		"SaveGameHeader"
	),
	"CommaSeparator": "",
	"DatObjclasses": (
		"PlayerInfo",
	),
	"DEBUG_MODE": False,
	"DoublePointSeparator": " ",
	"EnsureAscii": False,
	"EnteredPath": False,
	"Indent": "\t",
	"RTONExtensions": (
		".bin",
		".dat",
		".RTON",
		".rton"
	),
	"RTONNoExtensions": (
		"draper_",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"RepairFiles": False,
	"ShortNames": False,
	"SortKeys": False,
	"UncachedStrings": True
}

# Extra list class
class list2:
	def __init__(self, data):
		self.data = data

def error_message(string):
	if options["DEBUG_MODE"]:
		string = traceback.format_exc()
	
	fail.write(string + "\n")
	print("\33[91m%s\33[0m" % string)

# Data Types
false = b'\x00'
true = b'\x01'
rtid_id_string = b'\x02'
rtid_string = b'\x03'
int8 = b'\x08'
int8_zero = b'\x09'
uint8 = b'\x0a'
uint8_zero = b'\x0b'
int16 = b'\x10'
int16_zero = b'\x11'
uint16 = b'\x12'
uint16_zero = b'\x13'
int32 = b'\x20'
int32_zero = b'\x21'
floating_point = b'\x22'
floating_point_zero = b'\x23'
positive_int32_varint = b'\x24'
negative_int32_varint= b'\x25'
uint32 = b'\x26'
uint32_zero = b'\x27'
positive_uint32_varint = b'\x28'
negative_uint32_varint = b'\x29'
int64 = b'\x40'
int64_zero = b'\x41'
double = b'\x42'
double_zero = b'\x43'
positive_int64_varint = b'\x44'
negative_int64_varint = b'\x45'
uint64 = b'\x46'
uint64_zero = b'\x47'
positive_uint64_varint = b'\x48'
negative_uint64_varint = b'\x49'
latin_string = b'\x81'
utf8_string = b'\x82'
RTID = b'\x83'
RTID_empty = b'\x84'
object_start = b'\x85'
array = b'\x86'
cached_latin_string = b'\x90'
cached_latin_string_recall = b'\x91'
cached_utf8_string = b'\x92'
cached_utf8_string_recall = b'\x93'
array_start = b'\xfd'
array_end = b'\xfe'
object_end = b'\xff'

def encode_bool(boolean):
	if boolean == False:
		return false
	else:
		return true

def encode_number(integ):
	string=b""
	while integ or string == b"":
		if (integ > 127):
			string+=bytes([integ%128+128])
		else:
			string+=bytes([integ%128])
		
		integ=int(integ/128)
	
	return string

def encode_unicode(string):
	encoded_string = string.encode()
	return encode_number(len(string)) + encode_number(len(encoded_string)) + encoded_string

def encode_rtid(string):
	if '@' in string:
		name, type = string[5:-1].split('@')
		if name.count(".") == 2:
			i2, i1, i3 = name.split(".")
			name = encode_number(int(i1)) + encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
			encode = rtid_id_string
		else:
			name = encode_unicode(name)
			encode = rtid_string
		
		return RTID + encode + encode_unicode(type) + name
	else:
		return RTID + false

def encode_int(integ):
	if integ == 0:
		return int32_zero
	elif -129 < integ < 128:
		return encode_int8(integ)
	elif 0 < integ < 256:
		return encode_uint8(integ)
	elif -32769 < integ < 32768:
		return encode_int16(integ)
	elif 0 < integ < 65536:
		return encode_uint16(integ)
	elif -2147483649 < integ < 2147483648:
		return encode_int32(integ)
	elif 16777214 < integ < 4294967296:
		return encode_uint32(integ)
	elif -9223372036854775809 < integ < 9223372036854775808:
		return encode_int64(integ)
	elif 9223372036854775807 < integ < 18446744073709551616:
		return encode_uint64(integ)
	else:
		return encode_varint(integ)

def encode_varint(integ):
	if integ < 0:
		encode = negative_int32_varint
		integ*=-1
	else:
		encode = positive_int32_varint
	
	return encode+encode_number(integ)

def encode_int8(integ):
	return int8 + struct.pack('<b', integ)

def encode_uint8(integ):
	return uint8 + struct.pack('<B', integ)

def encode_int16(integ):
	return int16 + struct.pack('<h', integ)

def encode_uint16(integ):
	return uint16 + struct.pack('<H', integ)

def encode_int32(integ):
	return int32 + struct.pack('<i', integ)
	
def encode_uint32(integ):
	return uint32 + struct.pack('<I', integ)
	
def encode_int64(integ):
	return int64 + struct.pack('<q', integ)
	
def encode_uint64(integ):
	return uint64 + struct.pack('<Q', integ)

def encode_floating_point(dec):
	if dec == 0:
		return floating_point_zero
	elif dec != dec or dec == struct.unpack('<f', struct.pack("<f", dec))[0]:
		return floating_point + struct.pack("<f", dec)
	else:
		return double + struct.pack("<d", dec)

def encode_string(string, cached_latin_strings, cached_utf8_strings):
	if len(string) == len(string.encode('latin-1', 'ignore')):
		if options["UncachedStrings"]:
			data = latin_string + encode_number(len(string)) + string.encode('latin-1')
		elif not string in cached_latin_strings:
			cached_latin_strings.append(string)
			data = cached_latin_string + encode_number(len(string))+string.encode('latin-1')
		else:
			data = cached_latin_string_recall + encode_number(cached_latin_strings.index(string))
	else:
		if options["UncachedStrings"]:
			data = utf8_string + encode_unicode(string)
		elif not string in cached_utf8_strings:
			cached_utf8_strings.append(string)
			data = cached_utf8_string + encode_unicode(string)
		else:
			data = cached_utf8_string_recall + encode_number(cached_utf8_strings.index(string))
	
	return (data, cached_latin_strings, cached_utf8_strings)

def parse_array(data, cached_latin_strings, cached_utf8_strings):
	string = array + array_start + encode_number(len(data))
	for v in data:
		v, cached_latin_strings, cached_utf8_strings = parse_json(v, cached_latin_strings, cached_utf8_strings)
		string += v
	
	return (string + array_end, cached_latin_strings, cached_utf8_strings)

def parse_object(data, cached_latin_strings, cached_utf8_strings):
	string = object_start
	for v in data:
		key, value = v
		key, cached_latin_strings, cached_utf8_strings = encode_string(key, cached_latin_strings, cached_utf8_strings)
		value, cached_latin_strings, cached_utf8_strings = parse_json(value, cached_latin_strings, cached_utf8_strings)
		string += key + value
	
	return (string + object_end, cached_latin_strings, cached_utf8_strings)

def parse_json(data, cached_latin_strings, cached_utf8_strings):
	if isinstance(data, list):
		return parse_array(data, cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, list2):
		return parse_object(data.data, cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, bool):
		return (encode_bool(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, int):
		return (encode_int(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, float):
		return (encode_floating_point(data), cached_latin_strings, cached_utf8_strings)
	elif isinstance(data, str):
		if data == 'RTID(' + data[5:-1] + ')':
			return (encode_rtid(data), cached_latin_strings, cached_utf8_strings)
		else:
			return encode_string(data, cached_latin_strings, cached_utf8_strings)
	else:
		raise TypeError(type(data))

# Convert file
def conversion(inp, out):
	if os.path.isdir(inp) and os.path.realpath(inp) != os.path.realpath(pathout):
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			conversion(os.path.join(inp, entry), os.path.join(out, entry))
	elif os.path.isfile(inp) and inp.endswith(".json") and (options["AllowAllJSON"] or inp.endswith(options["RTONExtensions"], 0, -5) or os.path.basename(inp).startswith(options["RTONNoExtensions"])):
		write = out.removesuffix(".json")
		try:
			data = json.load(open(inp, 'rb'), object_pairs_hook = encode_object_pairs).data
		
		except Exception as e:
			error_message('%s in %s: %s' % (type(e).__name__, inp, e))
		else:
			try:
				data = b'RTON\x01\x00\x00\x00%sDONE' % parse_object(data, [], [])[0][1:]
				# No RTON extension
				if "" == os.path.splitext(write)[1] and not os.path.basename(write).startswith(options["RTONNoExtensions"]):
					vals = list(values_from_keys(data, ["objects","objclass"]))
					if any(value in vals for value in options["DatObjClasses"]):
						write += ".dat"
					elif any(value in vals for value in options["BinObjclasses"]):
						write += ".bin"
					else:
						write += ".rton"
				open(write, 'wb').write(data)
				print("wrote " + os.path.relpath(write, pathout))
			except Exception as e:
				error_message('%s in %s: %s' % (type(e).__name__, inp, e))

def encode_object_pairs(pairs):
	if options["SortKeys"]:
		pairs = sorted(pairs)
		
	return list2(pairs)

def values_from_keys(data, keyz):
	if keyz == []:
		yield data
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

try:
	fail = open(os.path.join(sys.path[0], "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")

	print("\033[95m\033[1mJSON RTONEncoder v1.1.0\n(C) 2021 by Nineteendo\033[0m\n")
	print("Working directory: " + os.getcwd())
	try:
		newoptions = json.load(open(os.path.join(sys.path[0], "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i) for i in newoptions[key]])
				elif key == "Indent" and type(newoptions[key]) in [int, type(None)]:
					options[key] = newoptions[key]
	except Exception as e:
		error_message("%s in options.json: %s" % (type(e).__name__, e))
	
	pathin = input("\033[1mInput file or directory\033[0m: ")
	if os.path.isfile(pathin):
		pathout = input("\033[1mOutput file\033[0m: ").removesuffix(".json")
	else:
		pathout = input("\033[1mOutput directory\033[0m: ")

	if not options["EnteredPath"]:
		pathin = pathin.replace("\\ ", " ").removesuffix(" ")
		pathout = pathout.replace("\\ ", " ").removesuffix(" ")
	
	# Start conversion
	start_time = datetime.datetime.now()
	conversion(pathin, pathout)
	print("Duration: %s" % (datetime.datetime.now() - start_time))
except BaseException as e:
	error_message("%s: %s" % (type(e).__name__, e))
fail.close()