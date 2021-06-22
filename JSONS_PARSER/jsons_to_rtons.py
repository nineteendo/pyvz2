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
		elif not string in cached_utf8_strings:
			cached_utf8_strings.append(string)
			return cached_UTF8_string + encode_unicode(string)
		else:
			return cached_UTF8_string_recall + encode_number(cached_utf8_strings.index(string))

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
			if ("objclass","WorldData") in data:
				objclass[0] = "WorldData"
			if ("objclass","WorldMapList") in data:
				objclass[0] = "WorldMapList"
			for v in data[:-1]:
				string += parse_json(v, oldkey)
			return string + object_end
	elif isinstance(data, tuple):
		key = data[0]
		value = data[1]
		if key == "objclass":
			objclass[0] = value
		if key == "uid" and not objclass[0] in ["WorldData","WorldMapList"] and len(value) > 11:
			objclass[1] = True
		if key in ["PlayerID", "SlotName", "QuestID", "QuestIssueDateString", "m_lastCompletedUniqueID", "m_lastCDNReceivedPushKey", "m_lastCDNReceivedPushVersion", "LastLevelPlayed", "LastMonetizationDate", "LastCashPurchaseObjectType",
		"LastGemPurchaseObjectType", "LastMintPurchaseObjectType", "LastCoinPurchaseObjectType", "wn", "wml", "lizg", "Reward1", "Reward2", "Reward3", "ConsecutiveLODReward", "FirstUnpurchasedPremiumPlantPlanted", "m_previousLevel",
		"m_collectableID_SunFromSky", "m_boardHolidayEventName", "m_activatedAudioEvent", "HelpedActivationSound", "m_musicTriggerOverride", "m_methodName", "m_activeAnimBaseLabel", "m_audioOnSlideIn", "m_audioOnSlideOut", "m_contentsTypeName",
		"AnimationLabel", "m_groundTrackName", "m_zombieType", "m_loadedResourceGroups", "m_availableSeeds", "m_loadingResourcesList", "m_autofillSeedTypes"] or oldkey == "m_lastStandLoadout" and key == "Level" or oldkey == "m_lootEntryInstancedData" and key == "UniqueId" or oldkey == "pr" and key == "n" or oldkey == "objdata" and key in ["l", "m_name"] or oldkey == "boarddata" and key == "m_level" or objclass[1] and key in ["uid", "TypeName", "PlantFoodActivationSound", "Key",
		"ProjectileLaunchSound", "SuggestionAlts", "Props", "zombieType", "LevelJam", "ZombieSpawnPattern", "LevelName", "ResourceGroups"]:
			special = 1 # uncached latin string 81
		if key in ["m_propertySheetName"] or oldkey == "objdata" and key == "n":
			special = 2 # uncached utf8 string 82
		if key in ["PlantRow", "GridSquareType", "GridSquareLocked", "MowerAllowedInRow"]:
			special = 3 # int8 08 and 09
		if key in ["W", "w", "pfco", "hter", "lm", "m_plantfoodCount", "m_plantfoodCountMax", "m_overrideInputPriority", "m_flagCount", "m_eyeIdleIndex", "m_packetCount", "pbi", "a", "rt", "m_conditionFlags", "m_targetFillPercent", "m_flagsTriggered"] or oldkey == "gpi" and key == "g": # or oldkey == "gpi" and key == "k" and value != 0
			special = 4 # uint8 0a and 0b
		if oldkey == "dli" and key in ["l", "r", "s"]:
			special =  5 # int16 10 and 11
		if key in ["E"] or oldkey == "dri" and key == "l" or oldkey == "e" and key == "i":
			special = 6 # uint16 12 and 13
		if key in ["rs", "LevelCRC", "m_type", "conw", "conl", "pay", "jcw", "jcl", "jsw", "jsl", "jll", "rcw", "rcl", "rczw", "rczl", "rze", "lsc", "rzw", "rza", "rzc", "tot", "StartingResolution",'alodet'] or oldkey == "lp" and key in ["s", "p"] or oldkey == "up" and key in ["i", "p"] or key == "ltfet" and 536870911 < value < 4294967296 or oldkey == "m_groundEffect" and key == "m_type" or key == "m_packetFlags" and isinstance(value, int) or oldkey in ["ap", "lp", "cqi", "puc", "qlgi"] and key == "i":
			special = 7 # uint32 26, 27, 28 and 29
		if key in ["QuestCompletionTime", "QuestLastPlayTime", "QuestEndTimeDisplayFallback", "LastDateQuestWasRecycled", "LastStoreOpenedTime", "LastStoreTablesUpdatedTime", "ts", "QuestIssueDate", "b", "m_localTimeOffsetFromServerTime", "b", "lst",
		"nst"] or oldkey == "qlgi" and key == "l" or oldkey in ["pbi", "gpi", "pli", "cqi"] and key == "t" or key == "ltfet" and 4294967295 < value < 9223372036854775808:
			special = 8 # int64 40, 41, 44 and 45
		if key in ["lspt", "lzgpt", "lodpt", "lpt", "lpurt", "lpurmt", "gp", "sp", "idx", "m_lastAgeResetTime", "m_inboxLatestMessageReadTime", "m_nextJoustFreePlayTime", "m_localJoustHighScore", "m_seasonNextDayPopupTime",
		"LastPennyFuelUpdatedTimeDelta", "PennyFuelUpdateStartTime", "LastZPSUpdatedTimeDelta", "ZPSUpdateStartTime", "ZombossUnlockedTime", "zgb", "sid", "rid", "rsid", "rpd0", "rpd1", "rpd2", "rznt", "ldco", "cllt", "cllst"] or key == "ltfet" and 9223372036854775807 < value < 18446744073709551616:
			special = 9 # uint64 46, 47, 48 and 49
		if key in ["NextScheduleTime", "NextDropTime"]:
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

def conversion(inp,out):
	if os.path.isdir(inp):
		os.makedirs(out, exist_ok=True)
		for entry in sorted(os.listdir(inp)):
			conversion(os.path.join(inp, entry),os.path.join(out, entry))
	elif not inp.endswith('.' + 'rton'):
		try:
			data=json.loads(open(inp, 'rb').read(), object_pairs_hook=parse_object_pairs)
		except:
			fail.write("\nno json:" + inp)
		else:
			try:
				cached_latin_strings[:] = []
				cached_utf8_strings[:] = []
				objclass[:] = ["",False]
				data=b'RTON\x01\x00\x00\x00'+parse_json(data)[1:]+b'DONE'
				if objclass[0] in ["DraperSaveData","GlobalSaveData","PlayerInfoLocalSaveData","LootSaveData","SaveGameHeader"]:
					extension = ".bin"
				elif objclass[0] == "PlayerInfo":
					extension = ".dat"
				else:
					extension = ".rton"
				write=os.path.splitext(out)[0]+extension
	
				open(write, 'wb').write(data)
				print("wrote " + write)
			except Exception as e:
				fail.write('\n' + str(type(e).__name__) + ': ' + inp + str(e))

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
	inp = "jsons/"
	out = "rtons/"
	os.makedirs(inp, exist_ok=True)

print(inp,">",out)
conversion(inp,out)
fail.close()
os.system("open fail.txt")