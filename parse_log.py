import re

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
			error_info = (row_index, chip_index, word_index, array_index)
			self.__error_list[unit_index].append(error_info)

	def get_error(self):
		return self.__error_list

	def get_error_in_unit(self, unit_index):
		return self.__error_list[unit_index]

	def get_error_in_word(self, row_index, unit_index, word_index):
		return filter(lambda x: x[0]==row_index and x[2] == word_index, self.get_error_in_unit(unit_index))

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

if __name__ == "__main__":
	chunk_list = []
	
	error_dict = read_log('log_samsung_2G_1600_A_modi_print_new_170313_test7 (5)')
	
	row_num = max(error_dict.keys())
	print row_num
	for _ in range(row_num / CHUNK_SIZE + 1):
		chunk_list.append(AddressChunk())

	for key, value in error_dict.iteritems():
		row_index = key % CHUNK_SIZE
		chunk_index = key / CHUNK_SIZE
		chunk_list[chunk_index].add_error(row_index, value)
	#print chunk_list[5].get_error()
	for chunk in chunk_list:
		#if 2 in chunk.get_error_in_word_hist().keys():
		print chunk.get_error_in_word_hist()
	#print chunk_list[8].get_error_in_word_hist()
