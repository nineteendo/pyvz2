# RTON parser (BETA!)
# written by 1Zulu and CLC2020

# usage: put rton files in rtons & run
import os, struct, time, json, binascii
from collections import OrderedDict

intern = []

# type 0a
def parse_uint8(fp):
	return struct.unpack('B', fp.read(1))[0]
	
# type 10
def parse_int16(fp):
	return struct.unpack('<h', fp.read(2))[0]

# type 12
def parse_uint16(fp):
	return struct.unpack('<H', fp.read(2))[0]
	
# type 26
def parse_uint32(fp):
	return struct.unpack('<I', fp.read(4))[0]

# type 20
def parse_int32(fp):
	return struct.unpack('<i', fp.read(4))[0]
	
# type 22
def parse_float(fp):
	return struct.unpack('<f', fp.read(4))[0]

# type 42
def parse_double(fp):
	return struct.unpack('<d', fp.read(8))[0]
	
# type 24 - varint (1-3 bytes)
def parse_varint(fp):
	result = 0;
	
	for i in range(4):
		num = struct.unpack('B', fp.read(1))[0]
		result += 128**i * (num & 0x7f)
		
		if num < 128:
			break
		
	return result
	
# helper for type string types
def parse_str_h(fp, sz):
		global x
		try:
				return str(struct.unpack('{0}s'.format(sz), fp.read(sz))[0], 'utf8')
		except:
				x=0
# types 81, 90, 91
def parse_str(fp, code):
	# returns interned string
	if code == b'\x91':
		i = parse_varint(fp)
		return intern[i]
		
	result = parse_str_h(fp, parse_varint(fp))
	if code == b'\x90':
		intern.append(result)
		#print(intern)
	
	return result

# type 82
def parse_str2(fp):
	i1 = parse_varint(fp)		
	i2 = parse_varint(fp)
	
	if i1 != i2:
		raise ValueError("type 82 or 83 has mismatched data sizes")
	
	return parse_str_h(fp, i1)

# type 83
def parse_ref(fp):
	ch = fp.read(1)
	
	if ch == b'\x00':
		return 'NULL'	
	elif ch == b'\x03':
		p1 = parse_str2(fp)
		p2 = parse_str2(fp)
	elif ch == b'\x02':
		p1 = parse_str2(fp)
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
	result = OrderedDict()
	
	try:
		while True:
			key = parse(fp)
			val = parse(fp, depth)
			
			result[key] = val			
	except StopIteration:
		pass

	return result
	
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
		def b2i(b):
				return '{0:x}'.format(struct.unpack('B', b)[0])
				
		mappings = {	
				b'\x20': parse_int32,
				b'\x21': lambda x: 0, 
				b'\x22': parse_float,
				b'\x23': lambda x: 0.0, 
				b'\x24': parse_varint,
								
				b'\x26': parse_uint32, 
				b'\x28': parse_varint, # don't really know what this is
				
				b'\x42': parse_double,
				
				b'\x82': parse_str2,
				b'\x83': parse_ref,
				
				b'\x85': parse_map,
				
				b'\x86': parse_list,
				b'\xff': stop_iteration 
				
		}
		
		# only in pp.dat
		ppdm = {

				b'\x08': parse_uint8,  
				b'\x09': lambda x: 0,
				
				b'\x0a': parse_uint8,  # 0b and 0a are related (ppd 04 vs 05)
				b'\x0b': lambda x: 0,
				
				b'\x10': parse_int16, # found in dli section of ppd
				b'\x11': lambda x: 0,  # 10 and 11 are related types (ppd)
				
				b'\x12': parse_uint16, # all found under the wmed['e'] in ppds
				b'\x13': lambda x: 0,
				
				# only in NoBackup RTONs
				b'\x27': lambda x: None,						
				b'\x45': parse_uint8,
				
		}
		
		unknown = {		
				b'\x41': 0
		}
		code = fp.read(1)
		# handle bool:
		if code in [b'\x00', b'\x01']:
				return code == b'\x01'
		# handle string types
		elif code in [b'\x81', b'\x90', b'\x91']:		
				return parse_str(fp, code)
		# move back
		elif code == b'\x84':
				return None
		# dafuq
		elif code == b'\x25':
				return -parse_varint(fp)
				
		# handle unknown types
		elif code in unknown:
				return raw_data(fp, code, unknown[code])	
		
		elif code == b'\x44':
				# handle DONE marker
				if fp.read(3) == b'ONE':
						raise StopIteration
				else:
						# this shit is only for pp.dat
						fp.seek(-3, 1)
						raw_data(fp, code, 5)
						
		elif code == b'\x85':
				return parse_map(fp, depth+1)
				
		elif code in [b'\x86']:
				return mappings[code](fp)
		
		elif code in ppdm:
				return ppdm[code](fp)
										
		else:
				return mappings[code](fp)
def conversion(inp,out):
	for entry in os.listdir(inp):
		pathin = os.path.join(inp, entry)
		pathout = os.path.join(out, entry)
		if os.path.isdir(pathin):
			try:
				os.mkdir(pathout)
			except:
				0
			conversion(pathin,pathout)
		elif not pathin.endswith('.' + 'json'):
			global x
			x=1
			# clear intern list
			intern[:] = []
			jfn=os.path.join(out,os.path.splitext(entry)[0]+'.json')
			fh=open(pathin, 'rb')
			try:
				if fh.read(8) == b'RTON\x01\x00\x00\x00':
					data=parse_map(fh)
					if x:
						open(jfn, 'w').write(json.dumps(data,indent=4))
						print('wrote '+format(jfn))
					else:
						fail.write('''
FAILED: '''+pathin)
				else:
					fail.write('''
NO RTON: '''+pathin)
			except KeyError as k:
				fail.write('''
KEY: ''' +pathin+' pos {0}: '.format(fh.tell())+str(k))
try:
	os.mkdir("jsons")
except:
	0
fail=open("fail.txt","w")
fail.write("fails:")
conversion("rtons","jsons")
fail.close()
os.system("open fail.txt")