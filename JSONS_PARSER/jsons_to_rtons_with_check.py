# JSON parser (ALPHA!)
# written by CLC2020
# usage: put json files in jsons & run

import os, json, struct

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
positive_varint_a = b'\x24'
negative_varint_a= b'\x25'
uint_32 = b'\x26'
uint_32_zero = b'\x27'
positive_varint_b = b'\28'
negative_varint_b = b'\29'

int64 = b'\40'
int64_zero = b'\41'
double = b'\x42'
double_zero = b'\x43'
positive_varint_c = b'\44'
negative_varint_c = b'\45'
uint_64 = b'\x46'
uint_64_zero = b'\x47'
positive_varint_c = b'\48'
negative_varint_c = b'\49'

latin_string = b'\81'
UTF8_string = b'\82'
RTID = b'\x83'
null = b'\x84'
object_start = b'\x85'
array = b'\x86'

cached_latin_string = b'\x90'
cached_latin_string_recall = b'\x91'
cached_UTF8_string = b'\x92'
cached_UTF8_string_recall = b'\x93'

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
	return encode_number(len(string))+encode_number(len(string.encode("utf-8")))+string.encode('utf-8')

def encode_string(string):
	if len(string) == len(string.encode('latin-1', 'ignore')):
		if not string in cached_latin_strings:
			cached_latin_strings.append(string)
			return cached_latin_string + encode_number(len(string))+string.encode('latin-1')
		else:
			return cached_latin_string_recall + encode_number(cached_latin_strings.index(string))
	else:
		if not string in cached_UTF8_strings:
			cached_UTF8_strings.append(string)
			return cached_UTF8_string + encode_unicode(string)
		else:
			return cached_UTF8_string_recall + encode_number(cached_UTF8_strings.index(string))

def encode_rtid(string):
	string = string[5:-1].split('@')
	name = string[0]
	type = string[-1]	
	return RTID + rtid_string + encode_unicode(type) + encode_unicode(name)

def encode_int(integ):
	if integ == 0:
		return int32_zero
	#elif -128 == integ:
	#	return encode_int8(integ)
	#elif 127 < integ < 256:
	#	return encode_uint8(integ)
	#elif -32769 < integ < -16383 or 16383 < integ < 32768:
	#	return encode_int16(integ)
	#elif 32767 < integ < 65536:
	#	return encode_uint16(integ)
	elif -2147483649 < integ < -268435455 or 268435455 < integ < 2147483648:
		return encode_int32(integ)
	#elif 2147483647 < integ < 4294967296:
	#	return encode_uint32(integ)
	#elif -9223372036854775809 < integ < -72057594037927936 or 72057594037927936 < integ < 9223372036854775808:
	#	return encode_int64(integ)
	#elif 9223372036854775807 < integ < 18446744073709551616:
	#	return encode_uint64(integ)
	else:
		return encode_varint(integ)

def encode_varint(integ):
	if integ < 0:
		encode=negative_varint_a
		integ*=-1
	else:
		encode=positive_varint_a
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
	return int64 + struct.pack('<l', integ)
	
def encode_uint64(integ):
	return uint64 + struct.pack('<L', integ)

def encode_floating_point(dec):
	if (dec == 0):
		return floating_point_zero
	elif dec == struct.unpack('<f', struct.pack("<f", dec))[0]:
		return floating_point + struct.pack("<f", dec)
	else:
		return double + struct.pack("<d", dec)

def parse_json(data):
	if isinstance(data, list):
		if len(data) == 0 or not isinstance(data[0], tuple):
			string = array+array_start+encode_number(len(data))
			for k, v in enumerate(data):
				string += parse_json(v)
			return string + array_end
		else:
			string = object_start
			for v in data[:-1]:
				string += parse_json(v)
			return string + object_end
	elif isinstance(data, tuple):
		return encode_string(data[0]) + parse_json(data[1])
	elif isinstance(data, bool):
		return encode_bool(data)
	if isinstance(data, int):
		return encode_int(data)
	elif isinstance(data, float):
		return encode_floating_point(data)
	elif data == None:
		return null
	elif isinstance(data, str):
		if data == 'RTID(' + data[5:-1] + ')' and '@' in data:
			return encode_rtid(data)
		else:
			return encode_string(data)
	else:
		raise TypeError(type(data))

def conversion(inp, out, check):
	for entry in sorted(os.listdir(inp)):
		pathin = os.path.join(inp, entry)
		pathout = os.path.join(out, entry)
		checkout = os.path.join(check, entry)
		if os.path.isdir(pathin):
			os.makedirs(pathout, exist_ok=True)
			os.makedirs(checkout, exist_ok=True)
			conversion(pathin,pathout,checkout)
		elif not pathin.endswith('.' + 'rton'):
			try:
				data=json.loads(open(pathin, 'rb').read(), object_pairs_hook=parse_object_pairs)
				base = os.path.splitext(entry)[0]+".rton"
				write=os.path.join(out,base)
			except:
				fail.write("\nno json:" + pathin)
			else:
				try:
					cached_latin_strings[:] = []
					cached_UTF8_strings[:] = []
					data=b'RTON\x01\x00\x00\x00'+parse_json(data)[1:]+b'DONE'
					
					open(write, 'wb').write(data)
					if (data == open(os.path.join(check,base), 'rb').read()):
						print("wrote " + format(write))
					else:	
						fail.write("\ndifferent rton:" + write)
				except Exception as e:
 					fail.write('\n' + str(type(e).__name__) + ': ' + pathin + str(e))

def parse_object_pairs(pairs):
	pairs.append(("",""))
	return pairs

cached_latin_strings=[]
cached_UTF8_strings=[]

os.makedirs("jsons", exist_ok=True)
os.makedirs("rtons", exist_ok=True)
os.makedirs("check", exist_ok=True)

fail=open("fail.txt","w")
fail.write("fails:")
conversion("jsons","rtons","check")
fail.close()
os.system("open fail.txt")