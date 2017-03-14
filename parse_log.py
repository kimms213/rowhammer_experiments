import re
from copy import deepcopy

# DRAM parameters
CHIP_NUM = 8
CAPACITY = 2 ** 34 # 16Gb
BANK_NUM = 2 ** 3
ROW_NUM  = 2 ** 15

# unit size
UNIT_SIZE = 2 ** 9
UNIT_NUM_PER_ROW = CAPACITY / (BANK_NUM * ROW_NUM * UNIT_SIZE)

# chunk size
CHUNK_SIZE = 32

# REMAP parameter
'''
# remap params of proposed scheme
REMAP_PARAMS = [
			0,	0,	0,	0,	0,	0,	0,	0 ,
			1,	3,	5,	7,	9,	11,	13,	15,
			2,	6,	10,	14,	18,	22,	26,	30,
			3,	9,	15,	21,	27,	1,	7,	13,
			4,	12,	20,	28,	4,	12,	20,	28,
			5,	15,	25,	3,	13,	23,	1,	11,
			6,	18,	30,	10,	22,	2,	14,	26,
			7,	21,	3,	17,	31,	13,	27,	9 ,
			8,	24,	8,	24,	8,	24,	8,	24,
			9,	27,	13,	31,	17,	3,	21,	7 ,
			10,	30,	18,	6,	26,	14,	2,	22,
			11,	4,	23,	13,	3,	25,	15,	5 ,
			12,	1,	28,	20,	12,	4,	28,	20,
			13,	7,	1,	27,	21,	15,	9,	3 ,
			14,	10,	6,	2,	30,	26,	22,	18,
			15,	13,	11,	9,	7,	5,	3,	1 ,
			16,	16,	16,	16,	16,	16,	16,	16,
			17,	19,	21,	23,	25,	27,	29,	31,
			18,	22,	26,	30,	2,	6,	10,	14,
			19,	25,	31,	5,	11,	17,	23,	29,
			20,	28,	4,	12,	20,	28,	4,	12,
			21,	31,	9,	19,	29,	7,	17,	27,
			22,	2,	14,	26,	6,	18,	30,	10,
			23,	5,	19,	1,	15,	29,	11,	25,
			24,	8,	24,	8,	24,	8,	24,	8 ,
			25,	11,	29,	15,	1,	19,	5,	23,
			26,	14,	2,	22,	10,	30,	18,	6 ,
			27,	17,	7,	29,	19,	9,	31,	21,
			28,	20,	12,	4,	28,	20,	12,	4 ,
			29,	23,	17,	11,	5,	31,	25,	19,
			30,	29,	22,	18,	14,	10,	6,	2 ,
			31,	26,	27,	25,	23,	21,	19,	17,
		]
'''

# remap params of patent
REMAP_PARAMS = [
			0,	0,	0,	0,	0,	0,	0,	0 ,
			1,	2,	4,	8,	16,	11,	13,	7 ,
			2,	4,	8,	16,	1,	22,	26,	14,
			3,	6,	12,	24,	17,	1,	7,	21,
			4,	8,	16,	1,	2,	12,	20,	28,
			5,	10,	20,	9,	18,	23,	1,	3 ,
			6,	12,	24,	17,	3,	2,	14,	10,
			7,	14,	28,	25,	19,	13,	27,	17,
			8,	16,	1,	2,	4,	24,	8,	24,
			9,	18,	5,	10,	20,	3,	21,	31,
			10,	20,	9,	18,	5,	14,	2,	6 ,
			11,	22,	13,	26,	21,	25,	15,	13,
			12,	24,	17,	3,	6,	4,	28,	20,
			13,	26,	21,	11,	22,	15,	9,	27,
			14,	28,	25,	19,	7,	26,	22,	2 ,
			15,	30,	29,	27,	23,	5,	3,	9 ,
			16,	1,	2,	4,	8,	16,	16,	16,
			17,	3,	6,	12,	24,	27,	29,	23,
			18,	5,	10,	20,	9,	6,	10,	30,
			19,	7,	14,	28,	25,	17,	23,	5 ,
			20,	9,	18,	5,	10,	28,	4,	12,
			21,	11,	22,	13,	26,	7,	17,	19,
			22,	13,	26,	21,	11,	18,	30,	26,
			23,	15,	30,	29,	27,	29,	11,	1 ,
			24,	17,	3,	6,	12,	8,	24,	8 ,
			25,	19,	7,	14,	28,	19,	5,	15,
			26,	21,	11,	22,	13,	30,	18,	22,
			27,	23,	15,	30,	29,	9,	31,	29,
			28,	25,	19,	7,	14,	20,	12,	4 ,
			29,	27,	23,	15,	30,	31,	25,	11,
			30,	29,	27,	23,	15,	10,	6,	18,
			31,	31,	31,	31,	31,	21,	19,	25,
		]

def read_log(log_file):
	#pattern = re.compile(r'Row\s(\d+)\s:\s((\(\d+[,]\d+[,]\d+\))+)')
	#pattern = re.compile(r'Row\s(\d+)\s:\s((\(\d+\,\s\d+\,\s\d+\))+)')
	pattern = re.compile(r'\[\!\]\sError\sposition\sin\sRow\s(\d+)\s:\s\(unit,\sindex,\sbit\)\s:\s((\(\d+,\s\d+,\s\d+\))+)')
	with open(log_file, 'rb') as log_file:
		lines = log_file.readlines()
		error_dict = {}
		for line in lines:
			m = pattern.match(line)
			if m:
				# get row index
				row_index = int(m.group(1))-1
				# get unit, byte, bit index
				error_index = []
				misc = m.group(2)
				misc_list = misc.split(')(')
				# trunc first, last index's ()
				misc_list[0] = misc_list[0][1:]
				misc_list[-1] = misc_list[-1][:-1]
				for item in misc_list:
					unit_index = int(item.split(',')[0])
					byte_index = int(item.split(',')[1])
					bit_index  = int(item.split(',')[2])
					error_index.append((unit_index, byte_index, bit_index))
				error_dict[row_index] = error_index

		return error_dict
				

class AddressChunk():
	''' This class stands for a chunk of 32 addresses, 
		which is the transformation unit
		stores the error location with respect to chip/array position
		***self.__error_list : [[(error_info) * error_Num] * UNIT_NUM_PER_ROW]
		error_info = (row_index, chip_index, word_index, array_index)
	'''
	def __init__(self):
		self.__error_list =  [[] for _ in  range(UNIT_NUM_PER_ROW)]
		self.__remapped_error_list =  [[] for _ in  range(UNIT_NUM_PER_ROW)]

	def add_error(self, row_index, error_index):
		# row index is between 0 and 31 (real_row_index % 32)
		for error_tuple in error_index:
			unit_index = error_tuple[0]
			byte_index = error_tuple[1]
			bit_index  = error_tuple[2]
			# chip index is determined as byte_index % CHIP_NUM
			chip_index = byte_index % CHIP_NUM
			word_index = byte_index / CHIP_NUM
			# array index is equal to bit_index
			array_index = bit_index
			error_info = [row_index, chip_index, word_index, array_index]
			self.__error_list[unit_index].append(error_info)

	def get_error(self):
		return self.__error_list

	def get_error_in_unit(self, unit_index):
		return self.__error_list[unit_index]

	def get_remapped_error_in_unit(self, unit_index):
		return self.__remapped_error_list[unit_index]

	def get_error_in_word(self, row_index, unit_index, word_index):
		return filter(lambda x: x[0]==row_index and x[2] == word_index, self.get_error_in_unit(unit_index))

	def get_remapped_error_in_word(self, row_index, unit_index, word_index):
		return filter(lambda x: x[0]==row_index and x[2] == word_index, self.get_remapped_error_in_unit(unit_index))		

	def get_error_in_word_hist(self):
		error_hist = {}
		for unit_index in range(len(self.__error_list)):
			for word_index in range(UNIT_SIZE / (CHIP_NUM * 8)):
				for row_index in range(CHUNK_SIZE):
					error_num = len(self.get_error_in_word(row_index, unit_index, word_index))
					if error_num in error_hist.keys():
						error_hist[error_num] += 1
					else:
						error_hist[error_num] = 1
		return error_hist

	def get_remapped_error_in_word_hist(self):
		error_hist = {}
		for unit_index in range(len(self.__remapped_error_list)):
			for word_index in range(UNIT_SIZE / (CHIP_NUM * 8)):
				for row_index in range(CHUNK_SIZE):
					error_num = len(self.get_remapped_error_in_word(row_index, unit_index, word_index))
					if error_num in error_hist.keys():
						error_hist[error_num] += 1
					else:
						error_hist[error_num] = 1
		return error_hist

	def remap(self):
		self.__remapped_error_list = deepcopy(self.__error_list)
		for unit in self.__remapped_error_list:
			for error_info in unit:
				row_index   = error_info[0]
				chip_index  = error_info[1]
				#word_index  = error_info[2]
				array_index = error_info[3]
				# remapping the row index
				error_info[0] = REMAP_PARAMS[row_index * CHIP_NUM + chip_index]
				error_info[0] = REMAP_PARAMS[error_info[0] * CHIP_NUM + array_index]
				

if __name__ == "__main__":
	chunk_list = []
	
	error_dict = read_log('log_files/log_samsung_2G_1600_A_modi_print_new_170313_test7 (6)')
	
	row_num = max(error_dict.keys())
	print row_num
	for _ in range(row_num / CHUNK_SIZE + 1):
		chunk_list.append(AddressChunk())

	for key, value in error_dict.iteritems():
		row_index = key % CHUNK_SIZE
		chunk_index = key / CHUNK_SIZE
		chunk_list[chunk_index].add_error(row_index, value)

	total_error = {}
	total_error_remapped = {}
	for chunk in chunk_list:
		chunk.remap()
		for key, value in chunk.get_error_in_word_hist().iteritems():
			if total_error.has_key(key):
				total_error[key] += value
			else:
				total_error[key] = value
		for key, value in chunk.get_remapped_error_in_word_hist().iteritems():
			if total_error_remapped.has_key(key):
				total_error_remapped[key] += value
			else:
				total_error_remapped[key] = value

		#total_error.update(chunk.get_error_in_word_hist())
		#total_error_remapped.update(chunk.get_remapped_error_in_word_hist())

		#if 2 in chunk.get_error_in_word_hist().keys():
		#print chunk.get_error_in_word_hist()
		#print chunk.get_remapped_error_in_word_hist()
	print total_error
	print total_error_remapped