# JSON parser (ALPHA!)
# written by CLC2020
# usage: put json files in jsons & run

import os, json, struct

false = b'\x00'
true = b'\x01'

uint8_a = b'\x08'
uint8_zero = b'\x09'
uint8_b = b'\x0a'
uint8_b_zero = b'\x0b'

int16 = b'\x10'
int16_zero = b'\x11'
uint16 = b'\x12'
uint16_zero = b'\x13'

int32 = b'\x20'
int32_zero = b'\x21'
floating_point = b'\x22'
floating_point_zero = b'\x23'
positive_varint = b'\x24'
negative_varint= b'\x25'
uint_32 = b'\x26'
uint_32_zero = b'\x27'
varint = b'\28'

unknown_data = b'\41'
double = b'\x42'

uint8_c = b'\x45'
uRTON_t = b'\x48'
RTON_t = b'\x49'

string2 = b'\82'
RTID = b'\x83'
null = b'\x84'
object_start = b'\x85'
array = b'\x86'

latin_string = b'\x90'
reused_latin_string = b'\x91'
UTF8_string = b'\x92'
reused_UTF8_string = b'\x93'

array_start = b'\xfd'
array_end = b'\xfe'
object_end = b'\xff'

def parse_object_pairs(pairs):
	pairs.append(("",""))
	return pairs

def encode_number(integ):
	string=b""
	while integ or string == b"":
		if (integ > 127):
			string+=bytes([integ%128+128])
		else:
			string+=bytes([integ%128])
		integ=int(integ/128)	
	return string

def encode_string(string):
	if len(string) == len(string.encode("latin-1")):
		if not string in latin_strings:
			latin_strings.append(string)
			return latin_string + encode_number(len(string))+string.encode('latin-1')
		else:
			return reused_latin_string + encode_number(latin_strings.index(string))
	else:
		if not string in UTF8_strings:
			UTF8_strings.append(string)
			return UTF8_string + encode_number(len(string))+string.encode('utf-8')
		else:
			return reused_UTF8_string + encode_number(UTF8_strings.index(string))


def encode_bool(boolean):
	if boolean == False:
		return false
	else:
		return true

def encode_int(integ):
	if integ == 0:
		return int32_zero
	elif -2097152 < integ < 2097152:
		return encode_varint(integ)
	elif -2147483648 < integ < 2147483647:
		return encode_int32(integ)
	else:
		raise TypeError(str(integ) + ' was too big.')	

def encode_varint(integ):
	if integ < 0:
		encode=negative_varint
		integ*=-1
	else:
		encode=positive_varint	
	return encode+encode_number(integ)

def encode_int32(integ):
	return int32 + struct.pack('<i', integ)

def encode_floating_point(dec):
	if (dec == 0):
		return floating_point_zero
	elif dec == struct.unpack('<f', struct.pack("<f", dec))[0]:
		return floating_point + struct.pack("<f", dec)
	else:
		return double + struct.pack("<d", dec)

def encode_rtid(string):
	string = string[5:-1].encode('utf-8').split(b'@')
	name = string[0]
	type = string[-1]
	return RTID + bytes([3]) + 2 * encode_number(len(type)) + type + 2 * encode_number(len(name)) + name

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

def conversion(inp, out):
	for entry in sorted(os.listdir(inp)):
		pathin = os.path.join(inp, entry)
		pathout = os.path.join(out, entry)
		if os.path.isdir(pathin):
			os.makedirs(pathout, exist_ok=True)
			conversion(pathin,pathout)
		elif not pathin.endswith('.' + 'rton'):
			try:
				data=json.loads(open(pathin, 'rb').read(), object_pairs_hook=parse_object_pairs)
				write=os.path.join(out,os.path.splitext(entry)[0]+'.rton')
			except:
				fail.write("\nno json:" + pathin)
			else:
				try:
					latin_strings[:] = []
					UTF8_strings[:] = []
					data=b'RTON\x01\x00\x00\x00'+parse_json(data)[1:]+b'DONE'
					
					open(write, 'wb').write(data)
					print("wrote " + format(write))
				except Exception as e:
 					fail.write('\n' + str(type(e).__name__) + ': ' + pathin + str(e))

latin_strings=[]
UTF8_strings=[]

os.makedirs("jsons", exist_ok=True)
os.makedirs("rtons", exist_ok=True)
fail=open("fail.txt","w")
fail.write("fails:")
conversion("jsons","rtons")
fail.close()
os.system("open fail.txt")