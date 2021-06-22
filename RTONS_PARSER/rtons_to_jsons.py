# RTON parser (BETA!)
# written by 1Zulu and CLC2020

# usage: put rton files in rtons & run
import os, struct, json

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
	
# type 24, 28, 44 and 48
def parse_varint(fp):
	result = 0;
	i = 0
	
	while i == 0 or num > 127:
		num = struct.unpack('B', fp.read(1))[0]
		result += 128**i * (num & 0x7f)
		i+=1
	return result

# type 25, 29, 45 and 49
def parse_negative_varint(fp):
	return -parse_varint(fp)

# type 26
def parse_uint32(fp):
	return struct.unpack('<I', fp.read(4))[0]

# type 40
def parse_int64(fp):
	return struct.unpack('<q', fp.read(4))[0]

# type 42
def parse_double(fp):
	return struct.unpack('<d', fp.read(8))[0]

# type 46
def parse_uint64(fp):
	return struct.unpack('<Q', fp.read(8))[0]
	
# types 81, 90
def parse_latin_str(fp):
	return fp.read(parse_varint(fp)).decode('latin-1')
	
# type 82, 92
def parse_utf8_str(fp):
	i1 = parse_varint(fp) # Character length
	string = fp.read(parse_varint(fp)).decode('utf-8')
	i2 = len(string)
	if i1 != i2:
		fail.write("\n	SilentError: %s pos %s: Unicode string of character length %s found, expected %s"%(fp.name,fp.tell()-1,i2,i1))
	return string
	
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
		return 'RTID()'	
	elif ch == b'\x03':
		p1 = parse_utf8_str(fp)
		p2 = parse_utf8_str(fp)
	elif ch == b'\x02':
		p1 = parse_utf8_str(fp)
		i2 = str(parse_varint(fp))
		i1 = str(parse_varint(fp))
		p2 = i1 + "." + i2 + "." + fp.read(4)[::-1].hex()
	else:
		raise ValueError("unexpected headbyte for type 83, found: {0}".format(str(ch)))		
	
	return 'RTID({0}@{1})'.format(p2, p1)

# type 85
def parse_map(fp):
	result = []
	
	try:
		while True:
			key = parse(fp)
			val = parse(fp)
			result.append((key,val))
	except KeyError as k:
		if k.args[0] == b'':
			fail.write("\n	SilentError: %s pos %s: End of file" %(fp.name,fp.tell()-1))
		else:
			raise k
	except StopIteration:
		pass
	
	return FakeDict(result)
# type 86
def parse_list(fp):	
	if fp.read(1) != b'\xfd':
		fail.write("\n	SilentError: %s pos %s: List is missing start marker" %(fp.name,fp.tell()-1))
	
	result = []
	i1 = 0
	i2 = parse_varint(fp)
	try:
		while True:
			result.append(parse(fp))
			i1+=1
	except KeyError as k:
		if k.args[0] == b'':
			fail.write("\n	SilentError: %s pos %s: End of file" %(fp.name,fp.tell()-1))
		else:
			raise k
	except StopIteration:
		if (i1 != i2):
			fail.write("\n	SilentError: %s pos %s: Array of length %s found, expected %s" %(fp.name,fp.tell()-1,i1,i2))
	
	return result

def end(fp):
	raise StopIteration

def parse(fp):
		
	mappings = {	
		b'\x00': lambda x: False,
		b'\x01': lambda x: True,
		b'\x20': parse_int32,
		b'\x21': lambda x: 0, # int32_zero
		b'\x22': parse_float,
		b'\x23': lambda x: 0.0, # float_zero
		b'\x24': parse_varint, # positive_int32_varint
		b'\x25': parse_negative_varint, # negative_int32_varint
		
		b'\x42': parse_double,
		
		b'\x83': parse_ref,
		b'\x84': lambda x: None, # None
		b'\x85': parse_map,
		b'\x86': parse_list,
		
		b'\xfe': end, 
		b'\xff': end
		
	}
	
	# only in pp.dat
	ppdm = {

		b'\x08': parse_int8,  
		b'\x09': lambda x: 0, # int8_zero
		b'\x0a': parse_uint8,
		b'\x0b': lambda x: 0, # uint8_zero
		
		b'\x10': parse_int16,
		b'\x11': lambda x: 0,  # int16_zero
		b'\x12': parse_uint16,
		b'\x13': lambda x: 0, # uint16_zero
		
		# only in NoBackup RTONs
		b'\x26': parse_uint32,
		b'\x27': lambda x: 0, #uint_32_zero
		b'\x28': parse_varint, # positive_uint32_varint
		b'\x29': parse_negative_varint, #negative_int32_varint
		
		b'\x41': lambda x: 0, #int64_zero
		
		b'\x44': parse_varint, # positive_int64_varint
		b'\x45': parse_negative_varint, # negative_int64_varint
		b'\x46': parse_uint64,
		b'\x47': lambda x: 0, # uint64_zero
		b'\x48': parse_varint, # positive_uint64_varint
		b'\x49': parse_negative_varint, # negative_uint64_varint
		
		b'\x81': parse_latin_str, # uncached string with roman characters
		b'\x82': parse_utf8_str, # uncached string with unicode characters
	}
	
	code = fp.read(1)
	# handle string types
	if code in [b'\x90', b'\x91', b'\x92', b'\x93']:
		return parse_cached_str(fp, code)
	# handle No_Backup
	elif code in ppdm:
		return ppdm[code](fp)
	else:
		return mappings[code](fp)
def conversion(inp,out):
	if os.path.isdir(inp):
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			conversion(os.path.join(inp, entry),os.path.join(out, entry))
	elif not inp.endswith('.' + 'json'):
		# clear cached_latin_strings
		cached_latin_strings[:] = []
		cached_utf8_strings[:] = []
		
		jfn=os.path.splitext(out)[0]+'.json'
		fh=open(inp, 'rb')
		try:
			if fh.read(8) == b'RTON\x01\x00\x00\x00':
				data=parse_map(fh)
				open(jfn, 'wb').write(json.dumps(data, ensure_ascii=False,indent=4).encode('utf8'))
				print('wrote '+format(jfn))
			else:
				fail.write('\nNO RTON: ' + inp)
		except Exception as e:
			fail.write('\n' + str(type(e).__name__) + ': ' + inp + ' pos {0}: '.format(fh.tell()-1)+str(e))

class FakeDict(dict):
	def __init__(self, items):
		self['something'] = 'something'
		self._items = items
	def items(self):
		return self._items

cached_latin_strings = []
cached_utf8_strings = []

fail=open("fail.txt","w")
fail.write("fails:")
try:
	inp = input("Input file or directory:")
	out = os.path.join(input("Output directory:"),os.path.basename(inp))
except:
	inp = "rtons/"
	out = "jsons/"
	os.makedirs(inp, exist_ok=True)

print(inp,">",out)
conversion(inp,out)
fail.close()
try:
	os.startfile("fail.txt")
except:
	try:
		os.system("open fail.txt")
	except:
		os.system("xdg-open fail.txt")