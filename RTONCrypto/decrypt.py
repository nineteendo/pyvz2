import copy, sys, datetime
from json import load
from os import listdir, makedirs, system
from os.path import dirname, isdir, isfile, join as osjoin, realpath, relpath
from traceback import format_exc
options = {
	"confirmPath": True,
	"DEBUG_MODE": True,
	"enteredPath": False,

	"encryption_key": "00000000000000000000000000000000"
}
def error_message(string):
# Print & log error
	if options["DEBUG_MODE"]:
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
		if options["enteredPath"]:
			string = newstring
		else:
			string = ""
			quoted = 0
			escaped = False
			tempstring = ""
			for char in newstring:
				if escaped:
					if quoted != 1 and char == "'" or quoted != 2 and char == '"' or quoted == 0 and char in "\\ ":
						string += tempstring + char
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
			if options["confirmPath"]:
				newstring = bold_input("Confirm \033[100m" + string)
	return string

# Encryption and decryption algorithm based on https://en.m.wikipedia.org/wiki/Advanced_Encryption_Standard
# Some definitions of this file storage algorithm
shifts = [
	[[0, 0], [1, 3], [2, 2], [3, 1]],
	[[0, 0], [1, 5], [2, 4], [3, 3]],
	[[0, 0], [1, 7], [3, 5], [4, 4]]
]

# [encryption_key_size][block_size] number of rounds
num_rounds = {
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

# padding way
class ZeroPadding:
	def __init__(self, block_size):
		self.block_size = block_size
	def decode(self, source):
		assert len(source) % self.block_size == 0
		offset = len(source)
		if offset == 0:
			return b''
		end = offset - self.block_size + 1

		while offset > end:
			offset -= 1
			if source[offset]:
				return source[:offset + 1]

		return source[:end]

class RijndaelCBC:
# Only CBC is defined, others are not necessary
	def __init__(self, block_size):
		if len(iv) not in (16, 24, 32):
			# The offset is not in these three and throws an exception
			raise ValueError('The iv you set (you set %s) is not within the definition requirements (16, 24, 32)!' % str(iv))
		if block_size not in (16, 24, 32):
			# Block size does not throw an exception in these three
			raise ValueError('The block_size you set (you set it as %s) is not within the definition requirement (16,24,32)!' % str(block_size))

		if len(encryption_key) not in (16, 24, 32):
			# encryption_key length is not in range throw exception
			raise ValueError('The encryption_key you set (you set %s) is not within the definition requirements (16, 24, 32)!' % str(len(encryption_key)))

		self.block_size = block_size
		rounds = num_rounds[len(encryption_key)][block_size]
		b_c = block_size // 4
		k_e = [[0] * b_c for _ in range(rounds + 1)]
		k_d = [[0] * b_c for _ in range(rounds + 1)]
		round_encryption_key_count = (rounds + 1) * b_c
		k_c = len(encryption_key) // 4
		tk = []
		for i in range(0, k_c):
			tk.append((ord(encryption_key[i * 4:i * 4 + 1]) << 24) | (ord(encryption_key[i * 4 + 1:i * 4 + 1 + 1]) << 16) |
					(ord(encryption_key[i * 4 + 2: i * 4 + 2 + 1]) << 8) | ord(encryption_key[i * 4 + 3:i * 4 + 3 + 1]))
		t = 0
		j = 0
		while j < k_c and t < round_encryption_key_count:
			k_e[t // b_c][t % b_c] = tk[j]
			k_d[rounds - (t // b_c)][t % b_c] = tk[j]
			j += 1
			t += 1
		r_con_pointer = 0
		while t < round_encryption_key_count:
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
			while j < k_c and t < round_encryption_key_count:
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
		self.padding = ZeroPadding(24)
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
		pt = self.padding.decode(ppt)
		return pt
	def x_or_block(self, b1, b2):
		i = 0
		r = bytes()
		while i < self.block_size:
			r += bytes([ord(b1[i:i+1]) ^ ord(b2[i:i+1])])
			i += 1
		return r

def conversion(inp, out, pathout):
# Recursive file convert function
	if isfile(inp) and inp.lower()[-8:] != ".decrypt":
		try:
			out += ".decrypt"
			file=open(inp,"rb")
			# skip magic value
			file.seek(2,0)
			cipher = rijndael_cbc.decrypt(file.read())
			file.close()
			open(out,"wb").write(cipher)
			print("wrote " + relpath(out, pathout))
		except Exception as e:
			error_message(type(e).__name__ + " in " + inp + ": " + str(e))
	elif isdir(inp):
		makedirs(out, exist_ok = True)
		for entry in listdir(inp):
			input_file = osjoin(inp, entry)
			if isfile(input_file) or input_file != pathout:
				conversion(input_file, osjoin(out, entry), pathout)

try:
	system("")
	if getattr(sys, "frozen", False):
		application_path = dirname(sys.executable)
	else:
		application_path = sys.path[0]
	fail = open(osjoin(application_path, "fail.txt"), "w")
	if sys.version_info[0] < 3:
		raise RuntimeError("Must be using Python 3")
	
	print("\033[95m\033[1mRTONDecryptor v1.1.2\n(C) 2022 by Nineteendo & SmallPea\033[0m\n")
	try:
		newoptions = load(open(osjoin(application_path, "options.json"), "rb"))
		for key in options:
			if key in newoptions and newoptions[key] != options[key]:
				if type(options[key]) == type(newoptions[key]):
					options[key] = newoptions[key]
				elif isinstance(options[key], tuple) and isinstance(newoptions[key], list):
					options[key] = tuple([str(i).lower() for i in newoptions[key]])
	except Exception as e:
		error_message(type(e).__name__ + " in options.json: " + str(e))
	
	encryption_key = str.encode(options["encryption_key"])
	iv = encryption_key[4: 28]
	rijndael_cbc = RijndaelCBC(24)
	
	encrypted_input = path_input("ENCRYPTED Input file or directory")
	if isfile(encrypted_input):
		encrypted_output = path_input("ENCRYPTED DECRYPTED Output file").removesuffix(".decrypt")
	else:
		encrypted_output = path_input("ENCRYPTED DECRYPTED Output directory")
	
	encrypted_dirname = dirname(encrypted_output)
	makedirs(encrypted_dirname, exist_ok = True)
	
	start_time = datetime.datetime.now()
	conversion(encrypted_input, encrypted_output, encrypted_dirname)
	green_print("finished decrypting in " + str(datetime.datetime.now() - start_time))
	if fail.tell() > 0:
		print("\33[93m" + "Errors occured, check: " + fail.name + "\33[0m")
	bold_input("\033[95mPRESS [ENTER]")
except Exception as e:
	error_message(type(e).__name__ + " : " + str(e))
except BaseException as e:
	warning_message(type(e).__name__ + " : " + str(e))
fail.close() # Close log