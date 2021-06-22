# RTON parser (BETA!)
# written by 1Zulu and CLC2020

# usage: put rton files in rtons & run
import os, struct, json

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
UTF8_string = b'\x82'
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

def encode_string(string, special = 0):
	if len(string) == len(string.encode('latin-1', 'ignore')) and special != 2:
		if special == 1:
			return latin_string + encode_number(len(string))+string.encode('latin-1')
		elif not string in cached_latin_strings:
			cached_latin_strings.append(string)
			return cached_latin_string + encode_number(len(string))+string.encode('latin-1')
		else:
			return cached_latin_string_recall + encode_number(cached_latin_strings.index(string))
	else:
		if special == 2:
			return UTF8_string + encode_unicode(string)
		elif not string in cached_UTF8_strings:
			cached_UTF8_strings.append(string)
			return cached_UTF8_string + encode_unicode(string)
		else:
			return cached_UTF8_string_recall + encode_number(cached_UTF8_strings.index(string))

def encode_rtid(string):
	if '@' in string:
		string = string[5:-1].split('@')
		name = string[0]
		if name.count(".") == 2:
			name = name.split(".")
			name = encode_number(int(name[1])) + encode_number(int(name[0])) + bytes.fromhex(name[2])[::-1]
			encode = rtid_id_string
		else:
			name = encode_unicode(name)
			encode = rtid_string
		type = string[-1]	
		return RTID + encode + encode_unicode(type) + name
	else:
		return RTID + false

def encode_int(integ, special = 0):
	if integ == 0:
		if special == 3:
			return int8_zero
		elif special == 4:
			return uint8_zero
		elif special == 5:
			return int16_zero
		elif special == 6:
			return uint16_zero
		elif special == 7:
			return uint32_zero
		elif special == 8:
			return int64_zero
		elif special == 9:
			return uint64_zero
		else:
			return int32_zero
	elif special == 3 and (-129 < integ < 128):
		return encode_int8(integ)
	elif special == 4 and (0 < integ < 256):
		return encode_uint8(integ)
	elif special == 5 and (-32769 < integ < 32768):
		return encode_int16(integ)
	elif special == 6 and (0 < integ < 65536):
		return encode_uint16(integ)
	elif special == 0 and (-2147483649 < integ < -2097150 or 2097150 < integ < 2147483648):
		return encode_int32(integ)
	elif special == 7 and (16777214 < integ < 4294967296):
		return encode_uint32(integ)
	elif special == 8 and (-9223372036854775809 < integ < -72057594037927936 or 72057594037927936 < integ < 9223372036854775808):
		return encode_int64(integ)
	elif special == 9 and (9223372036854775807 < integ < 18446744073709551616):
		return encode_uint64(integ)
	else:
		return encode_varint(integ, special)

def encode_varint(integ, special = 0):
	if integ < 0:
		if special == 7:
			encode = negative_uint32_varint
		elif special == 8:
			encode = negative_int64_varint
		elif special == 9:
			encode = negative_uint64_varint
		else:
			encode = negative_int32_varint
		integ*=-1
	else:
		if special == 7:
			encode = positive_uint32_varint
		elif special == 8:
			encode = positive_int64_varint
		elif special == 9:
			encode = positive_uint64_varint
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

def encode_floating_point(dec, special = 0):
	if (dec == 0):
		return floating_point_zero
	elif special != 10 and dec == struct.unpack('<f', struct.pack("<f", dec))[0]:
		return floating_point + struct.pack("<f", dec)
	else:
		return double + struct.pack("<d", dec)

def parse_json(data, oldkey = "", special = 0):
	if isinstance(data, list):
		if len(data) == 0 or not isinstance(data[0], tuple):
			string = array+array_start+encode_number(len(data))
			for k, v in enumerate(data):
				string += parse_json(v, oldkey, special)
			return string + array_end
		else:
			string = object_start
			for v in data[:-1]:
				string += parse_json(v, oldkey)
			return string + object_end
	elif isinstance(data, tuple):
		key = data[0]
		value = data[1]
		if key == "objclass":
			objclass[0] = value
		if key == "uid" and not value in ["2.0.06dcbdb1","2.0.05ac2eff","2.0.022f593c","2.0.0049e2bb","2.0.009807bc","2.0.0040a033","2.0.03d0c3b8","2.0.041196e0","2.0.07a4e595","2.0.0d808f14","2.0.0d9b671b","2.0.0470a981","2.0.0e46c3a8","2.0.0a20d660","2.0.004c6e93","2.0.0839b2e9","2.0.005ff25b","2.0.00a5c74a","2.0.06579702","2.0.072a44af","2.0.0535f1a2","2.0.00d4faf4","2.0.0d41f910","2.0.01561960","2.0.0005925a","2.0.017f766e","2.0.0031dd1d","2.0.0052346c","2.0.0e0e2f73","2.0.03899bee","2.0.0e6d6314","2.0.0ac76fc5","2.0.0c7ea8b7","2.0.0411b1c4","2.0.00ddd93d","2.0.0391496e","2.0.0380972f","2.0.0745556a","1.0.ffffffff","2.0.5c371969","2.0.3136bd51","2.0.3413bd93","2.0.74414528","2.0.f10a4528","2.0.11ca0953","2.0.199d14e3","2.0.1962c548","1.0.900cf319","1.0.77734805"] and len(value) > 11:
			print(value)
			objclass[1] = True
		if key in ["PlayerID","SlotName","QuestID","QuestIssueDateString","m_lastCompletedUniqueID","m_lastCDNReceivedPushKey","m_lastCDNReceivedPushVersion","LastLevelPlayed","LastMonetizationDate","LastCashPurchaseObjectType",
		"LastGemPurchaseObjectType","LastMintPurchaseObjectType","LastCoinPurchaseObjectType","wn","wml","lizg","Reward1","Reward2","Reward3","ConsecutiveLODReward","FirstUnpurchasedPremiumPlantPlanted","m_previousLevel",
		"m_collectableID_SunFromSky","m_boardHolidayEventName","m_activatedAudioEvent","HelpedActivationSound","m_musicTriggerOverride","m_methodName","m_activeAnimBaseLabel","m_audioOnSlideIn","m_audioOnSlideOut","m_contentsTypeName",
		"AnimationLabel","m_groundTrackName","m_zombieType","m_loadedResourceGroups","m_availableSeeds","m_loadingResourcesList","m_autofillSeedTypes"] or objclass[1] and key == "uid" or oldkey == "m_lastStandLoadout" and \
		key == "Level" or oldkey == "m_lootEntryInstancedData" and key == "UniqueId" or oldkey == "pr" and key == "n" or oldkey == "objdata" and key in ["l","m_name"] or objclass[0] == "SaveGameHeader" and key == "ResourceGroups" or \
		oldkey == "boarddata" and key == "m_level" or objclass[1] and key in ["TypeName","PlantFoodActivationSound", "Key", "ProjectileLaunchSound","SuggestionAlts","Props","zombieType","LevelJam","ZombieSpawnPattern","LevelName"]:
			special = 1 # uncached latin string 81
		if key in ["m_propertySheetName"] or oldkey == "objdata" and key == "n":
			special = 2 # uncached utf8 string 82
		if key in ["PlantRow","GridSquareType","GridSquareLocked","MowerAllowedInRow"]:
			special = 3 # int8 08 and 09
		if key in ["W","w","pfco","hter","lm","m_plantfoodCount","m_plantfoodCountMax","m_overrideInputPriority","m_flagCount","m_eyeIdleIndex","m_packetCount","pbi","a","rt","m_conditionFlags","m_targetFillPercent","m_flagsTriggered"] or \
		oldkey == "gpi" and key == "g": # or oldkey == "gpi" and key == "k" and value != 0
			special = 4 # uint8 0a and 0b
		if oldkey == "dli" and key in ["l","r","s"]:
			special =  5 # int16 10 and 11
		if key in ["E"] or oldkey == "dri" and key == "l" or oldkey == "e" and key == "i":
			special = 6 # uint16 12 and 13
		if key in ["rs","LevelCRC","m_type","conw","conl","pay","jcw","jcl","jsw","jsl","jll","rcw","rcl","rczw","rczl","rze","lsc","rzw","rza","rzc","tot","StartingResolution",'alodet'] or oldkey == "lp" and key in ["s","p"] or oldkey == \
		"up" and key in ["i","p"] or key == "ltfet" and 536870911 < value < 4294967296 or oldkey == "m_groundEffect" and key == "m_type" or key == "m_packetFlags" and isinstance(value, int) or oldkey in ["ap","lp","cqi","puc","qlgi"] and \
		key == "i":
			special = 7 # uint32 26, 27, 28 and 29
		if key in ["QuestCompletionTime","QuestLastPlayTime","QuestEndTimeDisplayFallback","LastDateQuestWasRecycled","LastStoreOpenedTime","LastStoreTablesUpdatedTime","ts","QuestIssueDate","b","m_localTimeOffsetFromServerTime","b","lst",
		"nst"] or oldkey == "qlgi" and key == "l" or oldkey in ["pbi","gpi","pli","cqi"] and key == "t" or key == "ltfet" and 4294967295 < value < 9223372036854775808:
			special = 8 # int64 40, 41, 44 and 45
		if key in ["lspt","lzgpt","lodpt","lpt","lpurt","lpurmt","gp","sp","idx","m_lastAgeResetTime","m_inboxLatestMessageReadTime","m_nextJoustFreePlayTime","m_localJoustHighScore","m_seasonNextDayPopupTime",
		"LastPennyFuelUpdatedTimeDelta","PennyFuelUpdateStartTime","LastZPSUpdatedTimeDelta","ZPSUpdateStartTime","ZombossUnlockedTime","zgb","sid","rid","rsid","rpd0","rpd1","rpd2","rznt","ldco","cllt","cllst"] or key == "ltfet" and \
		9223372036854775807 < value < 18446744073709551616:
			special = 9 # uint64 46, 47, 48 and 49
		if key in ["NextScheduleTime","NextDropTime"]:
			special = 10
		return encode_string(key) + parse_json(value, key, special)
	elif isinstance(data, bool):
		return encode_bool(data)
	if isinstance(data, int):
		return encode_int(data, special)
	elif isinstance(data, float):
		return encode_floating_point(data,special)
	elif data == None:
		return null
	elif isinstance(data, str):
		if data == 'RTID(' + data[5:-1] + ')':
			return encode_rtid(data)
		else:
			return encode_string(data,special)
	else:
		raise TypeError(type(data))

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
				w = json.dumps(data, ensure_ascii=False,indent=4).encode('utf8')
				open(jfn, 'wb').write(w)
				print('wrote '+format(jfn))
				objclass[:] = ["",False]
				cached_latin_strings[:] = []
				cached_utf8_strings[:] = []
				if open(inp, 'rb').read() != b'RTON\x01\x00\x00\x00'+parse_json(json.loads(w, object_pairs_hook=parse_object_pairs))[1:]+b'DONE':
					fail.write("\n	SilentError can't convert back from:" + inp)
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

def parse_object_pairs(pairs):
	pairs.append(("",""))
	return pairs

cached_latin_strings = []
cached_utf8_strings = []
objclass=[""]

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