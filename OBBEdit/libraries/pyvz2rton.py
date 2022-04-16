from io import BytesIO
from struct import unpack, pack, error
from json import dumps, load

cached_codes = [
	b"\x90",
	b"\x91",
	b"\x92",
	b"\x93"
]

class RTONDecoder():
	def __init__(self, comma = b",", doublePoint = b":", ensureAscii = False, fail = BytesIO(), indent = b"    ", repairFiles = True, sortKeys = False, sortValues = False):
		self.comma = comma
		self.doublePoint = doublePoint
		self.ensureAscii = ensureAscii
		self.fail = fail
		self.indent = indent
		self.repairFiles = repairFiles
		self.sortKeys = sortKeys
		self.sortValues = sortValues
	def root_object(self, fp, currrent_indent = b"\r\n"):
		VER = unpack("<I", fp.read(4))[0]
		string = b"{"
		new_indent = currrent_indent + self.indent
		items = []
		end = b"}"
		try:
			key, chached_strings, chached_printable_strings = self.parse(fp, new_indent, [], [])
			value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
			string += new_indent 
			items = [key + self.doublePoint + value]
			end = currrent_indent + end
			while True:
				key, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
				value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
				items.append(key + self.doublePoint + value)
		except KeyError as k:
			if str(k) == 'b""':
				if self.repairFiles:
					self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
				else:
					raise EOFError
			elif k.args[0] != b'\xff':
				raise TypeError("unknown tag " + k.args[0].hex())
		except (error, IndexError):
			if self.repairFiles:
				self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		if self.sortKeys:
			items = sorted(items)
		return string + (self.comma + new_indent).join(items) + end
	def warning_message(self, string):
	# Print & log warning
		self.fail.write("\t" + string + "\n")
		self.fail.flush()
		print("\33[93m" + string + "\33[0m")

	def parse_int8(self, fp):
	# type 08
		return repr(unpack("b", fp.read(1))[0]).encode()
	def parse_uint8(self, fp):
	# type 0a
		return repr(fp.read(1)[0]).encode()
	def parse_int16(self, fp):
	# type 10
		return repr(unpack("<h", fp.read(2))[0]).encode()
	def parse_uint16(self, fp):
	# type 12
		return repr(unpack("<H", fp.read(2))[0]).encode()
	def parse_int32(self, fp):
	# type 20
		return repr(unpack("<i", fp.read(4))[0]).encode()
	def parse_float(self, fp):
	# type 22
		return repr(unpack("<f", fp.read(4))[0]).replace("inf", "self.Infinity").replace("nan", "NaN").encode()
	def parse_uvarint(self, fp):
	# type 24, 28, 44 and 48
		return repr(self.parse_number(fp)).encode()
	def parse_varint(self, fp):
	# type 25, 29, 45 and 49
		num = self.parse_number(fp)
		if num % 2:
			num = -num -1
		return repr(num // 2).encode()
	def parse_number(self, fp):
		num = fp.read(1)[0]
		result = num & 0x7f
		i = 128
		while num > 127:
			num = fp.read(1)[0]
			result += i * (num & 0x7f)
			i *= 128
		return result
	def parse_uint32(self, fp):
	# type 26
		return repr(unpack("<I", fp.read(4))[0]).encode()
	def parse_int64(self, fp):
	# type 40
		return repr(unpack("<q", fp.read(8))[0]).encode()
	def parse_double(self, fp):
	# type 42
		return repr(unpack("<d", fp.read(8))[0]).replace("inf", "self.Infinity").replace("nan", "NaN").encode()
	def parse_uint64(self, fp):
	# type 46
		return repr(unpack("<Q", fp.read(8))[0]).encode()
	def parse_str(self, fp):
	# types 81, 90
		byte = fp.read(self.parse_number(fp))
		try:
			return dumps(byte.decode('utf-8'), ensure_ascii = self.ensureAscii).encode()
		except Exception:
			return dumps(byte.decode('latin-1'), ensure_ascii = self.ensureAscii).encode()
	def parse_printable_str(self, fp):
	# type 82, 92
		return dumps(self.parse_utf8_str(fp), ensure_ascii = self.ensureAscii).encode()
	def parse_utf8_str(self, fp):
		i1 = self.parse_number(fp) # Character length
		string = fp.read(self.parse_number(fp)).decode()
		i2 = len(string)
		if i1 != i2:
			self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": Unicode string of character length " + str(i2) + " found, expected " + str(i1))
		return string
	def parse_cached_str(self, fp, code, chached_strings, chached_printable_strings):
	# types 90, 91, 92, 93
		if code == b"\x90":
			result = self.parse_str(fp)
			chached_strings.append(result)
		elif code in b"\x91":
			result = chached_strings[self.parse_number(fp)]
		elif code in b"\x92":
			result = self.parse_printable_str(fp)
			chached_printable_strings.append(result)
		elif code in b"\x93":
			result = chached_printable_strings[self.parse_number(fp)]
		return (result, chached_strings, chached_printable_strings)
	def parse_ref(self, fp):
	# type 83
		ch = fp.read(1)
		if ch == b"\x00":
			return b'"RTID(0)"'
		elif ch == b"\x02":
			p1 = self.parse_utf8_str(fp)
			i2 = repr(self.parse_number(fp))
			i1 = repr(self.parse_number(fp))
			return dumps("RTID(" + i1 + "." + i2 + "." + fp.read(4)[::-1].hex() + "@" + p1 + ")", ensure_ascii = self.ensureAscii).encode()
		elif ch == b"\x03":
			p1 = self.parse_utf8_str(fp)
			return dumps("RTID(" + self.parse_utf8_str(fp) + "@" + p1 + ")", ensure_ascii = self.ensureAscii).encode()
		else:
			raise TypeError("unexpected subtype for type 83, found: " + ch.hex())
	def encode_object(self, fp, currrent_indent, chached_strings, chached_printable_strings):
	# type 85
		string = b"{"
		new_indent = currrent_indent + self.indent
		items = []
		end = b"}"
		try:
			key, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
			value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
			string += new_indent 
			items = [key + self.doublePoint + value]
			end = currrent_indent + end
			while True:
				key, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
				value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
				items.append(key + self.doublePoint + value)
		except KeyError as k:
			if str(k) == 'b""':
				if self.repairFiles:
					self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
				else:
					raise EOFError
			elif k.args[0] != b'\xff':
				raise TypeError("unknown tag " + k.args[0].hex())
		except (error, IndexError):
			if self.repairFiles:
				self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		if self.sortKeys:
			items = sorted(items)
		return (string + (self.comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
	def parse_list(self, fp, currrent_indent, chached_strings, chached_printable_strings):
	# type 86
		code = fp.read(1)
		if code == b"":
			if self.repairFiles:
				self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif code != b"\xfd":
			raise TypeError("List starts with " + code.hex())
		string = b"["
		new_indent = currrent_indent + self.indent
		items = []
		end = b"]"
		i1 = self.parse_number(fp)
		try:
			value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
			string += new_indent
			items = [value]
			end = currrent_indent + end
			while True:
				value, chached_strings, chached_printable_strings = self.parse(fp, new_indent, chached_strings, chached_printable_strings)
				items.append(value)
		except KeyError as k:
			if str(k) == 'b""':
				if self.repairFiles:
					self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
				else:
					raise EOFError
			elif k.args[0] != b'\xfe':
				raise TypeError("unknown tag " + k.args[0].hex())
		except (error, IndexError):
			if self.repairFiles:
				self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		i2 = len(items)
		if i1 != i2:
			self.warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() -1) + ": Array of length " + str(i1) + " found, expected " + str(i2))
		if self.sortValues:
			items = sorted(sorted(items), key = lambda key : len(key))
		
		return (string + (self.comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
	def parse(self, fp, current_indent, chached_strings, chached_printable_strings):
		code = fp.read(1)
		if code == b"\x85":
			return self.encode_object(fp, current_indent, chached_strings, chached_printable_strings)
		elif code == b"\x86":
			return self.parse_list(fp, current_indent, chached_strings, chached_printable_strings)
		elif code in cached_codes:
			return self.parse_cached_str(fp, code, chached_strings, chached_printable_strings)
		return (self.mappings[code](self, fp), chached_strings, chached_printable_strings)
	mappings = {
		b"\x00": lambda self, x: b"false",
		b"\x01": lambda self, x: b"true",
		b"\x08": parse_int8,  
		b"\x09": lambda self, x: b"0", # int8_zero
		b"\x0a": parse_uint8,
		b"\x0b": lambda self, x: b"0", # uint8_zero
		b"\x10": parse_int16,
		b"\x11": lambda self, x: b"0",  # int16_zero
		b"\x12": parse_uint16,
		b"\x13": lambda self, x: b"0", # uint16_zero
		b"\x20": parse_int32,
		b"\x21": lambda self, x: b"0", # int32_zero
		b"\x22": parse_float,
		b"\x23": lambda self, x: b"0.0", # float_zero
		b"\x24": parse_uvarint, # int32_uvarint
		b"\x25": parse_varint, # int32_varint
		b"\x26": parse_uint32,
		b"\x27": lambda self, x: b"0", #uint_32_zero
		b"\x28": parse_uvarint, # uint32_uvarint
		b"\x29": parse_varint, # uint32_varint?
		b"\x40": parse_int64,
		b"\x41": lambda self, x: b"0", #int64_zero
		b"\x42": parse_double,
		b"\x43": lambda self, x: b"0.0", # double_zero
		b"\x44": parse_uvarint, # int64_uvarint
		b"\x45": parse_varint, # int64_varint
		b"\x46": parse_uint64,
		b"\x47": lambda self, x: b"0", # uint64_zero
		b"\x48": parse_uvarint, # uint64_uvarint
		b"\x49": parse_varint, # uint64_varint
		b"\x81": parse_str, # uncached string
		b"\x82": parse_printable_str, # uncached printable string
		b"\x83": parse_ref,
		b"\x84": lambda self, x: b'"RTID(0)"' # zero reference
	}

class list2:
	# Extra list class
	def __init__(self, data):
		self.data = data

class JSONDecoder():
	def __init__(self):
		self.Infinity = [float("Infinity"), float("-Infinity")] # Inf and -inf values
	def parse_json(self, file):
	# JSON -> RTON
		data = load(file, object_pairs_hook = self.encode_object_pairs)
		cached_strings = {}
		string = b"RTON\x01\x00\x00\x00"
		for key, value in data.data:
			key, cached_strings = self.encode_string(key, cached_strings)
			value, cached_strings = self.encode_data(value, cached_strings)
			string += key + value
		return string + b"\xffDONE"
	def encode_object_pairs(self, pairs):
	# Object to list of tuples
		return list2(pairs)
	def encode_bool(self, boolean):
	# Boolian
		if boolean:
			return b"\x01"
		else:
			return b"\x00"
	def encode_number(self, integ):
	# Number with variable length
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
	def encode_unicode(self, string):
	# Unicode string
		encoded_string = string.encode()
		return self.encode_number(len(string)) + self.encode_number(len(encoded_string)) + encoded_string
	def encode_rtid(self, string):
	# RTID
		if "@" in string:
			name, type = string[5:-1].split("@")
			if name.count(".") == 2:
				i2, i1, i3 = name.split(".")
				return b"\x83\x02" + self.encode_unicode(type) + self.encode_number(int(i1)) + self.encode_number(int(i2)) + bytes.fromhex(i3)[::-1]
			else:
				return b"\x83\x03" + self.encode_unicode(type) + self.encode_unicode(name)
		else:
			return b"\x84"
	def encode_int(self, integ):
	# Number
		if integ == 0:
			return b"\x21"
		elif 0 <= integ <= 2097151:
			return b"\x24" + self.encode_number(integ)
		elif -1048576 <= integ <= 0:
			return b"\x25" + self.encode_number(-1 - 2 * integ)
		elif -2147483648 <= integ <= 2147483647:
			return b"\x20" + pack("<i", integ)
		elif 0 <= integ < 4294967295:
			return b"\x26" + pack("<I", integ)
		elif 0 <= integ <= 562949953421311:
			return b"\x44" + self.encode_number(integ)
		elif -281474976710656 <= integ <= 0:
			return b"\x45" + self.encode_number(-1 - 2 * integ)
		elif -9223372036854775808 <= integ <= 9223372036854775807:
			return b"\x40" + pack("<q", integ)
		elif 0 <= integ <= 18446744073709551615:
			return b"\x46" + pack("<Q", integ)
		elif 0 <= integ:
			return b"\x44" + self.encode_number(integ)
		else:
			return b"\x45" + self.encode_number(-1 - 2 * integ)
	def encode_float(self, dec):
	# Float
		if dec == 0:
			return b"\x23"
		elif dec != dec or dec in self.Infinity or -340282346638528859811704183484516925440 <= dec <= 340282346638528859811704183484516925440 and dec == unpack("<f", pack("<f", dec))[0]:
			return b"\x22" + pack("<f", dec)
		else:
			return b"\x42" + pack("<d", dec)
	def encode_string(self, string, cached_strings):
	# String
		if string in cached_strings:
			data = b"\x91" + self.encode_number(cached_strings[string])
		else:
			cached_strings[string] = len(cached_strings)
			encoded_string = string.encode()
			data = b"\x90" + self.encode_number(len(encoded_string)) + encoded_string
		return (data, cached_strings)
	def encode_array(self, data, cached_strings):
	# Array
		string = self.encode_number(len(data))
		for v in data:
			v, cached_strings = self.encode_data(v, cached_strings)
			string += v
		return (b"\x86\xfd" + string + b"\xfe", cached_strings)
	def encode_object(self, data, cached_strings):
	# Object
		string = b"\x85"
		for key, value in data:
			key, cached_strings = self.encode_string(key, cached_strings)
			value, cached_strings = self.encode_data(value, cached_strings)
			string += key + value
		return (string + b"\xff", cached_strings)
	def encode_data(self, data, cached_strings):
	# Data
		if isinstance(data, str):
			if "RTID()" == data[:5] + data[-1:]:
				return (self.encode_rtid(data), cached_strings)
			else:
				return self.encode_string(data, cached_strings)
		elif isinstance(data, bool):
			return (self.encode_bool(data), cached_strings)
		elif isinstance(data, int):
			return (self.encode_int(data), cached_strings)
		elif isinstance(data, float):
			return (self.encode_float(data), cached_strings)
		elif isinstance(data, list):
			return self.encode_array(data, cached_strings)
		elif isinstance(data, list2):
			return self.encode_object(data.data, cached_strings)
		elif data == None:
			return (b"\x84", cached_strings)
		else:
			raise TypeError(type(data))