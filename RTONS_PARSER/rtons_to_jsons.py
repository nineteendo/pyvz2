# RTON parser (BETA!)
# written by 1Zulu and CLC2020

# usage: put rton files in rtons & run
import os, struct, time, json, binascii
from collections import OrderedDict

cached_latin_strings = []
cached_utf8_strings = []

# type 08
def parse_int8(fp):
	return struct.unpack('b', fp.read(1))[0]

# type 0a
def parse_uint8(fp):
	return struct.unpack('B', fp.read(1))[0]
	
# type 10
def parse_int16(fp):
	return struct.unpack('<h', fp.read(2))[0]

# type 12
def parse_uint16(fp):
	return struct.unpack('<H', fp.read(2))[0]
	
# type 20
def parse_int32(fp):
	return struct.unpack('<i', fp.read(4))[0]

# type 22
def parse_float(fp):
	return struct.unpack('<f', fp.read(4))[0]
	
# type 24 - varint (1-3 bytes?)
def parse_varint(fp):
	result = 0;
	
	for i in range(4):
		num = struct.unpack('B', fp.read(1))[0]
		result += 128**i * (num & 0x7f)
		
		if num < 128:
			break
		
	return result

# type 26
def parse_uint32(fp):
	return struct.unpack('<I', fp.read(4))[0]

# type 40
def parse_int64(fp):
	return struct.unpack('<l', fp.read(8))[0]

# type 42
def parse_double(fp):
	return struct.unpack('<d', fp.read(8))[0]

# type 46
def parse_uint64(fp):
	return struct.unpack('<L', fp.read(8))[0]
	
# types 81, 90
def parse_latin_str(fp):
	return fp.read(parse_varint(fp)).decode('latin-1')
	
# type 82, 92
def parse_utf8_str(fp):
	parse_varint(fp) # Character length, only used when displaying text in game
	return fp.read(parse_varint(fp)).decode('utf-8')
	
# types 90, 91, 92, 93
def parse_cached_str(fp, code):
	if code == b'\x90':
		result = parse_latin_str(fp)
		cached_latin_strings.append(result)
	if code in b'\x91':
		i = parse_varint(fp)
		return cached_latin_strings[i]
	if code in b'\x92':
		result = parse_utf8_str(fp)
		cached_utf8_strings.append(result)
	if code in b'\x93':
		i = parse_varint(fp)
		return cached_utf8_strings[i]
	
	return result

# type 83
def parse_ref(fp):
	ch = fp.read(1)
	
	if ch == b'\x00':
		return 'NULL'	
	elif ch == b'\x03':
		p1 = parse_utf8_str(fp)
		p2 = parse_utf8_str(fp)
	elif ch == b'\x02':
		p1 = parse_utf8_str(fp)
		c = fp.read(1)
		if p1[0] == b'$':
			rb = 6
		else:
			rb = 5
		p2 = str(binascii.hexlify(c + fp.read(rb)), 'ascii')
	else:
		raise ValueError("unexpected headbyte for type 83, found: {0}".format(str(ch)))		
	
	return 'RTID({0}@{1})'.format(p2, p1)

# type 85
def parse_map(fp, depth=0):
	result = []
	
	try:
		while True:
			key = parse(fp)
			val = parse(fp, depth)
			
			result.append((key,val))			
	except StopIteration:
		pass
	
	return FakeDict(result)
	
def stop_iteration(fp):	
	raise StopIteration
	
# type 86
def parse_list(fp):	
	if fp.read(1) != b'\xfd':
		raise ValueError("list is missing start marker")
	
	result = []
	for i in range(parse_varint(fp)):
		result.append(parse(fp))
		
	if fp.read(1) != b'\xfe':
		raise ValueError("list is missing end marker")
	
	return result

def raw_data(fp, code, sz):
	return 'U{0}({1})'.format(str(binascii.hexlify(code), 'ascii'), str(binascii.hexlify(fp.read(sz)), 'ascii'))

def parse(fp, depth=0):
		
	mappings = {	
		b'\x20': parse_int32,
		b'\x21': lambda x: 0, #int32_zero
		b'\x22': parse_float,
		b'\x23': lambda x: 0.0, #float_zero
		b'\x24': parse_varint,
				
		b'\x26': parse_uint32,
		b'\x27': lambda x: 0,
		b'\x28': parse_varint,
		
		
		b'\x41': lambda x: 0, #int64_zero
		b'\x42': parse_double,
		
		b'\x81': parse_latin_str,
		b'\x82': parse_utf8_str,
		b'\x83': parse_ref,
		
		b'\x85': parse_map,
		b'\x86': parse_list,
		
		b'\xff': stop_iteration 
		
	}
	
	# only in pp.dat
	ppdm = {

		b'\x08': parse_int8,  
		b'\x09': lambda x: 0, # int8_zero
		
		b'\x0a': parse_uint8,  # 0b and 0a are related (ppd 04 vs 05)
		b'\x0b': lambda x: 0, # uint8_zero
		
		b'\x10': parse_int16, # found in dli section of ppd
		b'\x11': lambda x: 0,  # int16_zero
		
		b'\x12': parse_uint16, # all found under the wmed['e'] in ppds
		b'\x13': lambda x: 0, # uint16_zero
		
		# only in NoBackup RTONs
		b'\x27': lambda x: None, #uint_32_zero?	
		b'\x45': parse_uint8,
		
	}
	
	code = fp.read(1)
	# handle bool:
	if code in [b'\x00', b'\x01']:
		return code == b'\x01'
	# handle string types
	elif code in [b'\x90', b'\x91', b'\x92', b'\x93']:
		return parse_cached_str(fp, code)
	# move back
	elif code == b'\x84':
		return None
	# negative int
	elif code == b'\x25':
		return -parse_varint(fp)
	# DONE or raw data?
	elif code == b'\x44':
		# handle DONE marker
		if fp.read(3) == b'ONE':
			raise StopIteration
		else:
			# this is only for pp.dat
			fp.seek(-3, 1)
			raw_data(fp, code, 5)
	# Map		
	elif code == b'\x85':
		return parse_map(fp, depth+1)
	# pp.dat
	elif code in ppdm:
		return ppdm[code](fp)
				
	else:
		return mappings[code](fp)
def conversion(inp,out):
	for entry in sorted(os.listdir(inp)):
		pathin = os.path.join(inp, entry)
		pathout = os.path.join(out, entry)
		if os.path.isdir(pathin):
			os.makedirs(pathout, exist_ok=True)
			conversion(pathin,pathout)
		elif not pathin.endswith('.' + 'json'):
			# clear cached_latin_strings
			cached_latin_strings[:] = []
			cached_utf8_strings[:] = []
			
			jfn=os.path.join(out,os.path.splitext(entry)[0]+'.json')
			fh=open(pathin, 'rb')
			try:
				if fh.read(8) == b'RTON\x01\x00\x00\x00':
					data=parse_map(fh)
					open(jfn, 'wb').write(json.dumps(data, ensure_ascii=False,indent=4).encode('utf8'))
					print('wrote '+format(jfn))
				else:
					fail.write('\nNO RTON: '+pathin)
			except Exception as e:
 				print('\n' + str(type(e).__name__) + ': ' + pathin + ' pos {0}: '.format(fh.tell())+str(e))

class FakeDict(dict):
	def __init__(self, items):
		self['something'] = 'something'
		self._items = items
	def items(self):
		return self._items

os.makedirs("jsons", exist_ok=True)
os.makedirs("rtons", exist_ok=True)
fail=open("fail.txt","w")
fail.write("fails:")
conversion("rtons","jsons")
fail.close()
os.system("open fail.txt")