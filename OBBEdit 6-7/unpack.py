# Import libraries
from io import BytesIO
import sys, datetime, copy
from traceback import format_exc
from json import load, dumps
from struct import unpack, error
from zlib import decompress
from os import makedirs, listdir, system, getcwd, sep
from os.path import isdir, isfile, realpath, join as osjoin, dirname, relpath, basename, splitext

options = {
# Default options
	# SMF options
	"smfExtensions": (
		".rsb.smf",
	),
	"smfUnpackLevel": 1,
	# RSB options
	"rsbExtensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".rsb.smf",
		".obb"
	),
	"rsbUnpackLevel": 2,
	"rsgpEndsWith": (),
	"rsgpEndsWithIgnore": True,
	"rsgpStartsWith": (
		"packages",
		"worldpackages_"
	),
	"rsgpStartsWithIgnore": False,
	# RSGP options
	"endsWith": (
		".rton",
	),
	"endsWithIgnore": False,
	"rsgpExtensions": (
		".1bsr",
		".rsb1",
		".bsr",
		".rsb",
		".rsb.smf",
		".obb",
		".pgsr",
		".rsgp"
	),
	"rsgpUnpackLevel": 7,
	"startsWith": (
		"packages/",
	),
	"startsWithIgnore": False,
	# Encryption
	"encryptedExtensions": (
		".rton",
	),
	"encryptedUnpackLevel": 5,
	"encryptionKey": "00000000000000000000000000000000",
	# RTON options
	"comma": 0,
	"doublePoint": 1,
	"encodedUnpackLevel": 6,
	"ensureAscii": False,
	"indent": -1,
	"repairFiles": False,
	"RTONExtensions": (
		".bin",
		".dat",
		".json",
		".rton",
		".section"
	),
	"RTONNoExtensions": (
		"draper_",
		"local_profiles",
		"loot",
		"_saveheader_rton"
	),
	"sortKeys": False,
	"sortValues": False
}
def error_message(string):
# Print & log error
	string += "\n" + format_exc()
	fail.write(string + "\n")
	fail.flush()
	print("\033[91m" + string + "\033[0m")
def warning_message(string):
# Print & log warning
	fail.write("\t" + string + "\n")
	fail.flush()
	print("\33[93m" + string + "\33[0m")
def blue_print(text):
# Print in blue text
	print("\033[94m"+ text + "\033[0m")
def green_print(text):
# Print in green text
	print("\033[32m"+ text + "\033[0m")
def bold_input(text):
# Input in bold text
	return input("\033[1m"+ text + "\033[0m: ")
def path_input(text):
# Input hybrid path
	string = ""
	newstring = bold_input(text)
	while newstring or string == "":
		string = ""
		quoted = 0
		escaped = False
		tempstring = ""
		confirm = False
		for char in newstring:
			if escaped:
				if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
					string += tempstring + char
					confirm = True
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
			if confirm:
				newstring = bold_input("Confirm \033[100m" + string)
	return string
def input_level(text, minimum, maximum):
# Set input level for conversion
	try:
		return max(minimum, min(maximum, int(bold_input(text + "(" + str(minimum) + "-" + str(maximum) + ")"))))
	except Exception as e:
		error_message(type(e).__name__ + " : " + str(e))
		warning_message("Defaulting to " + str(minimum))
		return minimum
# RSGP Unpack functions
def rsgp_extract(rsgp_NAME, rsgp_OFFSET, file, out, pathout, level):
# Extract data from RGSP file
	if file.read(4) == b"pgsr":
		try:
			rsgp_VERSION = unpack("<I", file.read(4))[0]
			
			file.seek(8, 1)
			rsgp_TYPE = unpack("<I", file.read(4))[0]
			rsgp_BASE = unpack("<I", file.read(4))[0]

			DATA_OFFSET = unpack("<I", file.read(4))[0]
			COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
			if UNCOMPRESSED_SIZE != 0:
				file.seek(rsgp_OFFSET + DATA_OFFSET)
				if rsgp_TYPE == 3: # Compressed files
					blue_print("Decompressing ...")
					data = decompress(file.read(COMPRESSED_SIZE))
				else: # Uncompressed files
					data = file.read(COMPRESSED_SIZE)
			else:
				file.seek(4, 1)
				DATA_OFFSET = unpack("<I", file.read(4))[0]
				COMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				if UNCOMPRESSED_SIZE != 0:
					file.seek(rsgp_OFFSET + DATA_OFFSET)
					if rsgp_TYPE == 0: # Uncompressed files
						data = file.read(COMPRESSED_SIZE)
					else: # Compressed files
						blue_print("Decompressing ...")
						data = decompress(file.read(COMPRESSED_SIZE))
			if level < 5:
				file_path = osjoin(out, rsgp_NAME + ".section")
				makedirs(out, exist_ok = True)
				open(file_path, "wb").write(data)
				print("wrote " + relpath(file_path, pathout))
			else:
				file.seek(rsgp_OFFSET + 72)
				INFO_SIZE = unpack("<I", file.read(4))[0]
				INFO_OFFSET = rsgp_OFFSET + unpack("<I", file.read(4))[0]
				INFO_LIMIT = INFO_OFFSET + INFO_SIZE
				
				file.seek(INFO_OFFSET)
				DECODED_NAME = None
				NAME_DICT = {}
				while DECODED_NAME != "":
					FILE_NAME = b""
					temp = file.tell()
					for key in list(NAME_DICT.keys()):
						if NAME_DICT[key] + INFO_OFFSET < temp:
							NAME_DICT.pop(key)
						else:
							FILE_NAME = key
					BYTE = b""
					while BYTE != b"\x00":
						FILE_NAME += BYTE
						BYTE = file.read(1)
						LENGTH = 4 * unpack("<I", file.read(3) + b"\x00")[0]
						if LENGTH != 0:
							NAME_DICT[FILE_NAME] = LENGTH
					
					DECODED_NAME = FILE_NAME.decode().replace("\\", sep)
					NAME_CHECK = DECODED_NAME.replace("\\", "/").lower()
					PTX = unpack("<I", file.read(4))[0]
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					if PTX != 0:
						file.seek(20, 1)
						#A = unpack("<I", file.read(4))[0]
						#B = unpack("<I", file.read(4))[0]
						#C = unpack("<I", file.read(4))[0]
						#WIDHT = unpack("<I", file.read(4))[0]
						#HEIGHT = unpack("<I", file.read(4))[0]
					if DECODED_NAME and NAME_CHECK.startswith(startsWith) and NAME_CHECK.endswith(endsWith):
						file_data = data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE]
						if NAME_CHECK[-5:] == ".rton" and file_data[:2] == b"\x10\x00" and 5 < level:
							file_data = rijndael_cbc.decrypt(file_data[2:])
						if level < 7:
							file_path = osjoin(out, DECODED_NAME)
							makedirs(dirname(file_path), exist_ok = True)
							open(file_path, "wb").write(file_data)
							print("wrote " + relpath(file_path, pathout))
						elif NAME_CHECK[-5:] == ".rton":
							try:
								jfn = osjoin(out, DECODED_NAME[:-5] + ".JSON")
								makedirs(dirname(jfn), exist_ok = True)
								source = BytesIO(file_data)
								source.name = file.name + ": " + DECODED_NAME
								if source.read(4) == b"RTON":
									json_data = root_object(source, current_indent)
									open(jfn, "wb").write(json_data)
									print("wrote " + relpath(jfn, pathout))
								else:
									warning_message("No RTON " + source.name)
							except Exception as e:
								error_message(type(e).__name__ + " in " + file.name + ": " + DECODED_NAME + " pos " + str(source.tell() - 1) + ": " + str(e))
						#elif PTX:
						#	if FILE_SIZE == 4 * WIDHT * HEIGHT:
						#		file_path = osjoin(out, splitext(DECODED_NAME)[0] + ".PNG")
						#		makedirs(dirname(file_path), exist_ok = True)
						#		blue_print("Decoding ...")
						#		Image.frombuffer("RGBA", (WIDHT, HEIGHT), data[FILE_OFFSET: FILE_OFFSET + FILE_SIZE], "raw", COLORS, 0, 1).save("/Users/wannes/Documents/GitHub/PVZ2tools/PTXTests/ALWAYSLOADED_384_00.PNG")
						#		print("wrote " + relpath(file_path, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " while extracting " + rsgp_NAME + ".rsgp: " + str(e))
# decryption algorithm based on https://en.m.wikipedia.org/wiki/Advanced_Encryption_Standard
shifts = [
	[[0, 0], [1, 3], [2, 2], [3, 1]],
	[[0, 0], [1, 5], [2, 4], [3, 3]],
	[[0, 0], [1, 7], [3, 5], [4, 4]]
]
num_rounds = {
# [encryptionKeySize][block_size] number of rounds
	16: {16: 10, 24: 12, 32: 14},
	24: {16: 12, 24: 12, 32: 14},
	32: {16: 14, 24: 14, 32: 14}
}
A = [
	[1, 1, 1, 1, 1, 0, 0, 0],
	[0, 1, 1, 1, 1, 1, 0, 0],
	[0, 0, 1, 1, 1, 1, 1, 0],
	[0, 0, 0, 1, 1, 1, 1, 1],
	[1, 0, 0, 0, 1, 1, 1, 1],
	[1, 1, 0, 0, 0, 1, 1, 1],
	[1, 1, 1, 0, 0, 0, 1, 1],
	[1, 1, 1, 1, 0, 0, 0, 1]
]
# field GF(2^m) (generator = 3)
a_log = [1]
for i in range(255):
	j = (a_log[-1] << 1) ^ a_log[-1]
	if j & 0x100 != 0:
		j ^= 0x11B
	a_log.append(j)

log = [0] * 256
for i in range(1, 255):
	log[a_log[i]] = i

# Multiply by GF(2^m)
def mul(a, b):
	if a == 0 or b == 0:
		return 0
	return a_log[(log[a & 0xFF] + log[b & 0xFF]) % 255]

# F^{-1}(x)
box = [[0] * 8 for i in range(256)]
box[1][7] = 1
for i in range(2, 256):
	j = a_log[255 - log[i]]
	for t in range(8):
		box[i][t] = (j >> (7 - t)) & 0x01

B = [0, 1, 1, 0, 0, 0, 1, 1]

# box[i] <- B + A*box[i]
cox = [[0] * 8 for i in range(256)]
for i in range(256):
	for t in range(8):
		cox[i][t] = B[t]
		for j in range(8):
			cox[i][t] ^= A[t][j] * box[i][j]

S = [0] * 256
Si = [0] * 256
for i in range(256):
	S[i] = cox[i][0] << 7
	for t in range(1, 8):
		S[i] ^= cox[i][t] << (7-t)
	Si[S[i] & 0xFF] = i

# T-Box
G = [
	[2, 1, 1, 3],
	[3, 2, 1, 1],
	[1, 3, 2, 1],
	[1, 1, 3, 2]
]

AA = [[0] * 8 for i in range(4)]

for i in range(4):
	for j in range(4):
		AA[i][j] = G[i][j]
		AA[i][i+4] = 1

for i in range(4):
	pivot = AA[i][i]
	for j in range(8):
		if AA[i][j] != 0:
			AA[i][j] = a_log[(255 + log[AA[i][j] & 0xFF] - log[pivot & 0xFF]) % 255]
	for t in range(4):
		if i != t:
			for j in range(i+1, 8):
				AA[t][j] ^= mul(AA[i][j], AA[t][i])
			AA[t][i] = 0

iG = [[0] * 4 for i in range(4)]

for i in range(4):
	for j in range(4):
		iG[i][j] = AA[i][j + 4]

def mul4(a, bs):
	if a == 0:
		return 0
	rr = 0
	for b in bs:
		rr <<= 8
		if b != 0:
			rr = rr | mul(a, b)
	return rr

T1 = []
T2 = []
T3 = []
T4 = []
T5 = []
T6 = []
T7 = []
T8 = []
U1 = []
U2 = []
U3 = []
U4 = []

for t in range(256):
	s = S[t]
	T1.append(mul4(s, G[0]))
	T2.append(mul4(s, G[1]))
	T3.append(mul4(s, G[2]))
	T4.append(mul4(s, G[3]))

	s = Si[t]
	T5.append(mul4(s, iG[0]))
	T6.append(mul4(s, iG[1]))
	T7.append(mul4(s, iG[2]))
	T8.append(mul4(s, iG[3]))

	U1.append(mul4(t, iG[0]))
	U2.append(mul4(t, iG[1]))
	U3.append(mul4(t, iG[2]))
	U4.append(mul4(t, iG[3]))

r_con = [1]
r = 1
for t in range(1, 30):
	r = mul(2, r)
	r_con.append(r)

class RijndaelCBC:
# Only CBC is defined, others are not necessary
	def __init__(self, block_size):
		if len(iv) not in (16, 24, 32):
			# The offset is not in these three and throws an exception
			raise ValueError('The iv you set (you set %s) is not within the definition requirements (16, 24, 32)!' % str(iv))
		if block_size not in (16, 24, 32):
			# Block size does not throw an exception in these three
			raise ValueError('The block_size you set (you set it as %s) is not within the definition requirement (16,24,32)!' % str(block_size))

		if len(encryptionKey) not in (16, 24, 32):
			# encryptionKey length is not in range throw exception
			raise ValueError('The encryptionKey you set (you set %s) is not within the definition requirements (16, 24, 32)!' % str(len(encryptionKey)))

		self.block_size = block_size
		rounds = num_rounds[len(encryptionKey)][block_size]
		b_c = block_size // 4
		k_e = [[0] * b_c for _ in range(rounds + 1)]
		k_d = [[0] * b_c for _ in range(rounds + 1)]
		roundEncryptionKeyCount = (rounds + 1) * b_c
		k_c = len(encryptionKey) // 4
		tk = []
		for i in range(0, k_c):
			tk.append((ord(encryptionKey[i * 4:i * 4 + 1]) << 24) | (ord(encryptionKey[i * 4 + 1:i * 4 + 1 + 1]) << 16) |
					(ord(encryptionKey[i * 4 + 2: i * 4 + 2 + 1]) << 8) | ord(encryptionKey[i * 4 + 3:i * 4 + 3 + 1]))
		t = 0
		j = 0
		while j < k_c and t < roundEncryptionKeyCount:
			k_e[t // b_c][t % b_c] = tk[j]
			k_d[rounds - (t // b_c)][t % b_c] = tk[j]
			j += 1
			t += 1
		r_con_pointer = 0
		while t < roundEncryptionKeyCount:
			tt = tk[k_c - 1]
			tk[0] ^= (S[(tt >> 16) & 0xFF] & 0xFF) << 24 ^ \
					(S[(tt >> 8) & 0xFF] & 0xFF) << 16 ^ \
					(S[tt & 0xFF] & 0xFF) << 8 ^ \
					(S[(tt >> 24) & 0xFF] & 0xFF) ^ \
					(r_con[r_con_pointer] & 0xFF) << 24
			r_con_pointer += 1
			if k_c != 8:
				for i in range(1, k_c):
					tk[i] ^= tk[i - 1]
			else:
				for i in range(1, k_c // 2):
					tk[i] ^= tk[i - 1]
				tt = tk[k_c // 2 - 1]
				tk[k_c // 2] ^= (S[tt & 0xFF] & 0xFF) ^ \
								(S[(tt >> 8) & 0xFF] & 0xFF) << 8 ^ \
								(S[(tt >> 16) & 0xFF] & 0xFF) << 16 ^ \
								(S[(tt >> 24) & 0xFF] & 0xFF) << 24
				for i in range(k_c // 2 + 1, k_c):
					tk[i] ^= tk[i - 1]
			j = 0
			while j < k_c and t < roundEncryptionKeyCount:
				k_e[t // b_c][t % b_c] = tk[j]
				k_d[rounds - (t // b_c)][t % b_c] = tk[j]
				j += 1
				t += 1
		for r in range(1, rounds):
			for j in range(b_c):
				tt = k_d[r][j]
				k_d[r][j] = (
					U1[(tt >> 24) & 0xFF] ^
					U2[(tt >> 16) & 0xFF] ^
					U3[(tt >> 8) & 0xFF] ^
					U4[tt & 0xFF]
				)
		self.Ke = k_e
		self.Kd = k_d
	def decrypt(self, cipher):
		assert len(cipher) % self.block_size == 0
		ppt = bytes()
		offset = 0
		v = iv
		while offset < len(cipher):
			block = cipher[offset:offset + self.block_size]
			if len(block) != self.block_size:
				raise ValueError(
					'The self.block_size: %s you set does not match the current block data size: %s' % (
						str(self.block_size),
						str(len(block))
					)
				)

			k_d = self.Kd
			b_c = self.block_size // 4
			rounds = len(k_d) - 1
			if b_c == 4:
				s_c = 0
			elif b_c == 6:
				s_c = 1
			else:
				s_c = 2
			s1 = shifts[s_c][1][1]
			s2 = shifts[s_c][2][1]
			s3 = shifts[s_c][3][1]
			a = [0] * b_c
			t = [0] * b_c
			for i in range(b_c):
				t[i] = (ord(block[i * 4: i * 4 + 1]) << 24 |
						ord(block[i * 4 + 1: i * 4 + 1 + 1]) << 16 |
						ord(block[i * 4 + 2: i * 4 + 2 + 1]) << 8 |
						ord(block[i * 4 + 3: i * 4 + 3 + 1])) ^ k_d[0][i]
			for r in range(1, rounds):
				for i in range(b_c):
					a[i] = (T5[(t[i] >> 24) & 0xFF] ^
							T6[(t[(i + s1) % b_c] >> 16) & 0xFF] ^
							T7[(t[(i + s2) % b_c] >> 8) & 0xFF] ^
							T8[t[(i + s3) % b_c] & 0xFF]) ^ k_d[r][i]
				t = copy.copy(a)
			result = []
			for i in range(b_c):
				tt = k_d[rounds][i]
				result.append((Si[(t[i] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
				result.append((Si[(t[(i + s1) % b_c] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
				result.append((Si[(t[(i + s2) % b_c] >> 8) & 0xFF] ^ (tt >> 8)) & 0xFF)
				result.append((Si[t[(i + s3) % b_c] & 0xFF] ^ tt) & 0xFF)
			decrypted = bytes()
			for xx in result:
				decrypted += bytes([xx])
			ppt += self.x_or_block(decrypted, v)
			offset += self.block_size
			v = block
		
		# padding way
		assert len(ppt) % self.block_size == 0
		offset = len(ppt)
		if offset == 0:
			return b''
		end = offset - self.block_size + 1

		while offset > end:
			offset -= 1
			if ppt[offset]:
				return ppt[:offset + 1]

		return ppt[:end]
	def x_or_block(self, b1, b2):
		i = 0
		r = bytes()
		while i < self.block_size:
			r += bytes([ord(b1[i:i+1]) ^ ord(b2[i:i+1])])
			i += 1
		return r
def file_to_folder(inp, out, level, extensions, pathout):
# Recursive file convert function
	if isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in sorted(listdir(inp)):
			input_file = osjoin(inp, entry)
			output_file = osjoin(out, entry)
			if isfile(input_file):
				file_to_folder(input_file, splitext(output_file)[0], level, extensions, pathout)
			elif input_file != pathout:
				file_to_folder(input_file, output_file, level, extensions, pathout)
	elif isfile(inp) and inp.lower().endswith(extensions):
		try:
			file = open(inp, "rb")
			HEADER = file.read(4)
			if HEADER == b"\xD4\xFE\xAD\xDE":
				UNCOMPRESSED_SIZE = unpack("<I", file.read(4))[0]
				blue_print("Decompressing ...")
				data = decompress(file.read())
				if level < 3:
					open(out, "wb").write(data)
					print("wrote " + relpath(out, pathout))
				else:
					file = BytesIO(data)
					file.name = inp
					HEADER = file.read(4)
			if HEADER == b"1bsr":
				file.seek(40)
				FILES = unpack("<I", file.read(4))[0]
				DATA_OFFSET = unpack("<I", file.read(4))[0]
				file.seek(DATA_OFFSET)
				for i in range(0, FILES):
					FILE_NAME = file.read(128).strip(b"\x00").decode()
					FILE_CHECK = FILE_NAME.lower()
					FILE_OFFSET = unpack("<I", file.read(4))[0]
					FILE_SIZE = unpack("<I", file.read(4))[0]
					
					file.seek(68, 1)
					if FILE_CHECK.startswith(rsgpStartsWith) and FILE_CHECK.endswith(rsgpEndsWith):
						temp = file.tell()
						file.seek(FILE_OFFSET)
						if level < 4:
							makedirs(out, exist_ok = True)
							open(osjoin(out, FILE_NAME + ".rsgp"), "wb").write(file.read(FILE_SIZE))
							print("wrote " + relpath(osjoin(out, FILE_NAME + ".rsgp"), pathout))
						else:
							rsgp_extract(FILE_NAME, FILE_OFFSET, file, out, pathout, level)
						file.seek(temp)
			elif HEADER == b"pgsr":
				file.seek(0)
				rsgp_extract("data", 0, file, out, pathout, level)
		except Exception as e:
			error_message("Failed OBBUnpack: " + type(e).__name__ + " in " + inp + " pos " + str(file.tell()) + ": " + str(e))
# RTON Decode functions
def parse_int8(fp):
# type 08
	return repr(unpack("b", fp.read(1))[0]).encode()
def parse_uint8(fp):
# type 0a
	return repr(fp.read(1)[0]).encode()
def parse_int16(fp):
# type 10
	return repr(unpack("<h", fp.read(2))[0]).encode()
def parse_uint16(fp):
# type 12
	return repr(unpack("<H", fp.read(2))[0]).encode()
def parse_int32(fp):
# type 20
	return repr(unpack("<i", fp.read(4))[0]).encode()
def parse_float(fp):
# type 22
	return repr(unpack("<f", fp.read(4))[0]).replace("inf", "Infinity").replace("nan", "NaN").encode()
def parse_uvarint(fp):
# type 24, 28, 44 and 48
	return repr(parse_number(fp)).encode()
def parse_varint(fp):
# type 25, 29, 45 and 49
	num = parse_number(fp)
	if num % 2:
		num = -num -1
	return repr(num // 2).encode()
def parse_number(fp):
	num = fp.read(1)[0]
	result = num & 0x7f
	i = 128
	while num > 127:
		num = fp.read(1)[0]
		result += i * (num & 0x7f)
		i *= 128
	return result
def parse_uint32(fp):
# type 26
	return repr(unpack("<I", fp.read(4))[0]).encode()
def parse_int64(fp):
# type 40
	return repr(unpack("<q", fp.read(8))[0]).encode()
def parse_double(fp):
# type 42
	return repr(unpack("<d", fp.read(8))[0]).replace("inf", "Infinity").replace("nan", "NaN").encode()
def parse_uint64(fp):
# type 46
	return repr(unpack("<Q", fp.read(8))[0]).encode()
def parse_str(fp):
# types 81, 90
	byte = fp.read(parse_number(fp))
	try:
		return dumps(byte.decode('utf-8'), ensure_ascii = ensureAscii).encode()
	except Exception:
		return dumps(byte.decode('latin-1'), ensure_ascii = ensureAscii).encode()
def parse_printable_str(fp):
# type 82, 92
	return dumps(parse_utf8_str(fp), ensure_ascii = ensureAscii).encode()
def parse_utf8_str(fp):
	i1 = parse_number(fp) # Character length
	string = fp.read(parse_number(fp)).decode()
	i2 = len(string)
	if i1 != i2:
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": Unicode string of character length " + str(i2) + " found, expected " + str(i1))
	return string
def parse_cached_str(fp, code, chached_strings, chached_printable_strings):
# types 90, 91, 92, 93
	if code == b"\x90":
		result = parse_str(fp)
		chached_strings.append(result)
	elif code in b"\x91":
		result = chached_strings[parse_number(fp)]
	elif code in b"\x92":
		result = parse_printable_str(fp)
		chached_printable_strings.append(result)
	elif code in b"\x93":
		result = chached_printable_strings[parse_number(fp)]
	return (result, chached_strings, chached_printable_strings)
def parse_ref(fp):
# type 83
	ch = fp.read(1)
	if ch == b"\x00":
		return b'"RTID(0)"'
	elif ch == b"\x02":
		p1 = parse_utf8_str(fp)
		i2 = repr(parse_number(fp))
		i1 = repr(parse_number(fp))
		return dumps("RTID(" + i1 + "." + i2 + "." + fp.read(4)[::-1].hex() + "@" + p1 + ")", ensure_ascii = ensureAscii).encode()
	elif ch == b"\x03":
		p1 = parse_utf8_str(fp)
		return dumps("RTID(" + parse_utf8_str(fp) + "@" + p1 + ")", ensure_ascii = ensureAscii).encode()
	else:
		raise TypeError("unexpected subtype for type 83, found: " + ch.hex())
def root_object(fp, currrent_indent):
# root object
	VER = unpack("<I", fp.read(4))[0]
	string = b"{"
	new_indent = currrent_indent + indent
	items = []
	end = b"}"
	try:
		key, chached_strings, chached_printable_strings = parse(fp, new_indent, [], [])
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent 
		items = [key + doublePoint + value]
		end = currrent_indent + end
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(key + doublePoint + value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xff':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	if sortKeys:
		items = sorted(items)
	return string + (comma + new_indent).join(items) + end
def parse_object(fp, currrent_indent, chached_strings, chached_printable_strings):
# type 85
	string = b"{"
	new_indent = currrent_indent + indent
	items = []
	end = b"}"
	try:
		key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent 
		items = [key + doublePoint + value]
		end = currrent_indent + end
		while True:
			key, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(key + doublePoint + value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xff':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	if sortKeys:
		items = sorted(items)
	return (string + (comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
def parse_list(fp, currrent_indent, chached_strings, chached_printable_strings):
# type 86
	code = fp.read(1)
	if code == b"":
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	elif code != b"\xfd":
		raise TypeError("List starts with " + code.hex())
	string = b"["
	new_indent = currrent_indent + indent
	items = []
	end = b"]"
	i1 = parse_number(fp)
	try:
		value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
		string += new_indent
		items = [value]
		end = currrent_indent + end
		while True:
			value, chached_strings, chached_printable_strings = parse(fp, new_indent, chached_strings, chached_printable_strings)
			items.append(value)
	except KeyError as k:
		if str(k) == 'b""':
			if repairFiles:
				warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
			else:
				raise EOFError
		elif k.args[0] != b'\xfe':
			raise TypeError("unknown tag " + k.args[0].hex())
	except (error, IndexError):
		if repairFiles:
			warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() - 1) + ": end of file")
		else:
			raise EOFError
	i2 = len(items)
	if i1 != i2:
		warning_message("SilentError: " + fp.name + " pos " + str(fp.tell() -1) + ": Array of length " + str(i1) + " found, expected " + str(i2))
	if sortValues:
		items = sorted(sorted(items), key = lambda key : len(key))
	
	return (string + (comma + new_indent).join(items) + end, chached_strings, chached_printable_strings)
def parse(fp, current_indent, chached_strings, chached_printable_strings):
	code = fp.read(1)
	if code == b"\x85":
		return parse_object(fp, current_indent, chached_strings, chached_printable_strings)
	elif code == b"\x86":
		return parse_list(fp, current_indent, chached_strings, chached_printable_strings)
	elif code in cached_codes:
		return parse_cached_str(fp, code, chached_strings, chached_printable_strings)
	return (mappings[code](fp), chached_strings, chached_printable_strings)
cached_codes = [
	b"\x90",
	b"\x91",
	b"\x92",
	b"\x93"
]
mappings = {	
	b"\x00": lambda x: b"false",
	b"\x01": lambda x: b"true",
	b"\x08": parse_int8,  
	b"\x09": lambda x: b"0", # int8_zero
	b"\x0a": parse_uint8,
	b"\x0b": lambda x: b"0", # uint8_zero
	b"\x10": parse_int16,
	b"\x11": lambda x: b"0",  # int16_zero
	b"\x12": parse_uint16,
	b"\x13": lambda x: b"0", # uint16_zero
	b"\x20": parse_int32,
	b"\x21": lambda x: b"0", # int32_zero
	b"\x22": parse_float,
	b"\x23": lambda x: b"0.0", # float_zero
	b"\x24": parse_uvarint, # int32_uvarint
	b"\x25": parse_varint, # int32_varint
	b"\x26": parse_uint32,
	b"\x27": lambda x: b"0", #uint_32_zero
	b"\x28": parse_uvarint, # uint32_uvarint
	b"\x29": parse_varint, # uint32_varint?
	b"\x40": parse_int64,
	b"\x41": lambda x: b"0", #int64_zero
	b"\x42": parse_double,
	b"\x43": lambda x: b"0.0", # double_zero
	b"\x44": parse_uvarint, # int64_uvarint
	b"\x45": parse_varint, # int64_varint
	b"\x46": parse_uint64,
	b"\x47": lambda x: b"0", # uint64_zero
	b"\x48": parse_uvarint, # uint64_uvarint
	b"\x49": parse_varint, # uint64_varint
	b"\x81": parse_str, # uncached string
	b"\x82": parse_printable_str, # uncached printable string
	b"\x83": parse_ref,
	b"\x84": lambda x: b'"RTID(0)"' # zero reference
}
def conversion(inp, out, pathout, extensions, noextensions):
# Recursive file convert function
	check = inp.lower()
	if isfile(inp) and (check.endswith(extensions) or basename(check).startswith(noextensions)):
		try:
			file = open(inp, "rb")
			HEADER = file.read(2)
			if HEADER == b"\x10\x00":
				open(out,"wb").write(rijndael_cbc.decrypt(file.read()))
				print("wrote " + relpath(out, pathout))
			elif HEADER == b"RT" and file.read(2) == b"ON":
				if out.lower()[-5:] == ".rton":
					out = out[:-5]
				out += ".json"
				data = root_object(file, current_indent)
				open(out, "wb").write(data)
				print("wrote " + relpath(out, pathout))
			elif check[-5:] != ".json":
				warning_message("No RTON " + inp)
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + " pos " + str(file.tell() -1) + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout, extensions, noextensions)
# Start of the code
try:
	system("")
	if getattr(sys, "frozen", False):
		application_path = dirname(sys.executable)
	else:
		application_path = sys.path[0]
	fail = open(osjoin(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mOBBUnpacker v1.1.4\n(C) 2022 by Nineteendo, Luigi Auriemma, Small Pea, 1Zulu, YingFengTingYu & h3x4n1um\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
				elif key == "indent" and newoptions[key] == None:
					options[key] = newoptions[key]
	except Exception as e:
		error_message(type(e).__name__ + " in options.json: " + str(e))
	
	if options["smfUnpackLevel"] < 1:
		options["smfUnpackLevel"] = input_level("SMF Unpack Level", 1, 2)
	if options["rsbUnpackLevel"] < 1:
		options["rsbUnpackLevel"] = input_level("OBB/RSB/SMF Unpack Level", 2, 3)
	if options["rsgpUnpackLevel"] < 1:
		options["rsgpUnpackLevel"] = input_level("RSGP/OBB/RSB/SMF Unpack Level", 3, 7)
	if options["encryptedUnpackLevel"] < 1:
		options["encryptedUnpackLevel"] = input_level("ENCRYPTED Unpack Level", 5, 6)
	if options["encodedUnpackLevel"] < 1:
		options["encodedUnpackLevel"] = input_level("ENCODED Unpack Level", 6, 7)

	if options["rsgpStartsWithIgnore"]:
		rsgpStartsWith = ""
	else:
		rsgpStartsWith = options["rsgpStartsWith"]
	if options["rsgpEndsWithIgnore"]:
		rsgpEndsWith = ""
	else:
		rsgpEndsWith = options["rsgpEndsWith"]

	encryptionKey = str.encode(options["encryptionKey"])
	iv = encryptionKey[4: 28]
	rijndael_cbc = RijndaelCBC(24)
	if options["endsWithIgnore"]:
		endsWith = ""
	else:
		endsWith = options["endsWith"]
	if options["startsWithIgnore"]:
		startsWith = ""
	else:
		startsWith = options["startsWith"]

	if options["comma"] > 0:
		comma = b"," + b" " * options["comma"]
	else:
		comma = b","
	if options["doublePoint"] > 0:
		doublePoint = b":" + b" " * options["doublePoint"]
	else:
		doublePoint = b":"
	if options["indent"] == None:
		indent = current_indent = b""
	elif options["indent"] < 0:
		current_indent = b"\r\n"
		indent = b"\t"
	else:
		current_indent = b"\r\n"
		indent = b" " * options["indent"]
	ensureAscii = options["ensureAscii"]
	repairFiles = options["repairFiles"]
	sortKeys = options["sortKeys"]
	sortValues = options["sortValues"]
	
	level_to_name = ["SPECIFY", "SMF", "RSB", "RSGP", "SECTION", "ENCRYPTED", "ENCODED", "DECODED (beta)"]

	blue_print("Working directory: " + getcwd())
	if 2 >= options["smfUnpackLevel"] > 1:
		smf_input = path_input("SMF Input file or directory")
		if isfile(smf_input):
			smf_output = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Output file")
		else:
			smf_output = path_input("SMF " + level_to_name[options["smfUnpackLevel"]] + " Output directory")
	if 3 >= options["rsbUnpackLevel"] > 2:
		rsb_input = path_input("OBB/RSB/SMF Input file or directory")
		rsb_output = path_input("OBB/RSB/SMF " + level_to_name[options["rsbUnpackLevel"]] + " Output directory")
	if 7 >= options["rsgpUnpackLevel"] > 3:
		rsgp_input = path_input("RSGP/OBB/RSB/SMF Input file or directory")
		rsgp_output = path_input("RSGP/OBB/RSB/SMF " + level_to_name[options["rsgpUnpackLevel"]] + " Output directory")
	if 6 >= options["encryptedUnpackLevel"] > 5:
		encrypted_input = path_input("ENCRYPTED Input file or directory")
		if isfile(encrypted_input):
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output file")
		else:
			encrypted_output = path_input("ENCRYPTED " + level_to_name[options["encryptedUnpackLevel"]] + " Output directory")
	if 7 >= options["encodedUnpackLevel"] > 6:
		encoded_input = path_input("ENCODED Input file or directory")
		if isfile(encoded_input):
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output file")
		else:
			encoded_output = path_input("ENCODED " + level_to_name[options["encodedUnpackLevel"]] + " Output directory")
			if encoded_output.lower()[:-5] == ".json":
				encoded_output = encoded_output[:-5]

	# Start file_to_folder
	start_time = datetime.datetime.now()
	if 2 >= options["smfUnpackLevel"] > 1:
		file_to_folder(smf_input, smf_output, options["smfUnpackLevel"], options["smfExtensions"], dirname(smf_output))
	if 3 >= options["rsbUnpackLevel"] > 2:
		file_to_folder(rsb_input, rsb_output, options["rsbUnpackLevel"], options["rsbExtensions"], rsb_output)
	if 7 >= options["rsgpUnpackLevel"] > 3:
		file_to_folder(rsgp_input, rsgp_output, options["rsgpUnpackLevel"], options["rsgpExtensions"], rsgp_output)
	if 6 >= options["encryptedUnpackLevel"] > 5:
		conversion(encrypted_input, encrypted_output, dirname(encrypted_output), options["encryptedExtensions"], ())
	if 7 >= options["encodedUnpackLevel"] > 6:
		conversion(encoded_input, encoded_output, dirname(encoded_output), options["RTONExtensions"], options["RTONNoExtensions"])

	green_print("finished unpacking in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log