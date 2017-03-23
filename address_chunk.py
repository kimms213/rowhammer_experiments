from copy import deepcopy
from operator import add

# import user modules
from utils import PARAMS
from mapper import Mapper

class AddressChunk():
	''' This class stands for a chunk of 32 addresses, 
		which is the transformation unit
		stores the error location with respect to chip/array position
		***self.__error_list : [[(error_info) * error_Num] * UNIT_NUM_PER_ROW]
		error_info = (row_index, chip_index, word_index, array_index)
	'''
	def __init__(self):
		self.__error_list =  [[] for _ in  range(PARAMS['unit_num'])]
		self.__remapped_error_list =  [[] for _ in  range(PARAMS['unit_num'])]

	def add_error(self, row_index, error_index):
		# row index is between 0 and 31 (real_row_index % 32)
		for error_tuple in error_index:
			unit_index = error_tuple[0]
			byte_index = error_tuple[1]
			bit_index  = error_tuple[2]
			# chip index is determined as byte_index % CHIP_NUM
			chip_index = byte_index % PARAMS['chip_num']
			word_index = byte_index / PARAMS['chip_num']
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

	def get_error_in_byte(self, row_index, unit_index, chip_index, word_index):
		return filter(lambda x: x[0]==row_index and x[1]==chip_index and x[2] == word_index, self.get_error_in_unit(unit_index))

	def get_remapped_error_in_word(self, row_index, unit_index, word_index):
		return filter(lambda x: x[0]==row_index and x[2] == word_index, self.get_remapped_error_in_unit(unit_index))

	def get_remapped_error_in_byte(self, row_index, unit_index, chip_index, word_index):
		return filter(lambda x: x[0]==row_index and x[1]==chip_index and x[2] == word_index, self.get_remapped_error_in_unit(unit_index))

	def get_error_in_word_hist(self):
		error_hist = {}
		for unit_index in range(len(self.__error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					error_num = len(self.get_error_in_word(row_index, unit_index, word_index))
					if error_num in error_hist.keys():
						error_hist[error_num] += 1
					else:
						error_hist[error_num] = 1
		return error_hist

	def get_double_error_in_word(self):
		error_list = []
		for unit_index in range(len(self.__error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					error_in_word = self.get_error_in_word(row_index, unit_index, word_index)
					error_num = len(error_in_word)
					if error_num >= 2:
						error_list.append(error_in_word)
		return error_list

	def get_double_error_in_byte(self):
		error_list = []
		for unit_index in range(len(self.__error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					for chip_index in range(PARAMS['chip_num']):
						error_in_word = self.get_error_in_byte(row_index, unit_index, chip_index, word_index)
						error_num = len(error_in_word)
						if error_num >= 2:
							error_list.append(error_in_word)
		return error_list

	def get_remapped_error_in_word_hist(self):
		error_hist = {}
		for unit_index in range(len(self.__remapped_error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					error_num = len(self.get_remapped_error_in_word(row_index, unit_index, word_index))
					if error_hist.has_key(error_num):
						error_hist[error_num] += 1
					else:
						error_hist[error_num] = 1
		return error_hist

	def get_remapped_double_error_in_word(self):
		error_list = []
		for unit_index in range(len(self.__remapped_error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					error_in_word = self.get_remapped_error_in_word(row_index, unit_index, word_index)
					error_num = len(error_in_word)
					if error_num >= 2:
						error_list.append(error_in_word)
		return error_list

	def get_remapped_double_error_in_byte(self):
		error_list = []
		for unit_index in range(len(self.__remapped_error_list)):
			for word_index in range(PARAMS['unit_size'] / (PARAMS['chip_num'] * 8)):
				for row_index in range(PARAMS['chunk_size']):
					for chip_index in range(PARAMS['chip_num']):
						error_in_word = self.get_remapped_error_in_byte(row_index, unit_index, chip_index, word_index)
						error_num = len(error_in_word)
						if error_num >= 2:
							error_list.append(error_in_word)
		return error_list

	def remap(self, remap_params_row):
		self.__remapped_error_list = deepcopy(self.__error_list)
		for unit in self.__remapped_error_list:
			for error_info in unit:
				row_index   = error_info[0]
				chip_index  = error_info[1]
				word_index  = error_info[2]
				bit_index = error_info[3]

				# First level remap (remapping the row index)
				error_info[0] = remap_params_row[row_index * PARAMS['chip_num'] + chip_index]

	# for double(or triple) remapping 
	def remap_more(self, remap_params_row, remap_params_bit):
		self.__remapped_error_list = deepcopy(self.__error_list)
		for unit in self.__remapped_error_list:
			for error_info in unit:
				row_index   = error_info[0]
				chip_index  = error_info[1]
				word_index  = error_info[2]
				bit_index = error_info[3]

				# First level remap (remapping the row index)
				error_info[0] = remap_params_row[row_index * PARAMS['chip_num'] + chip_index]
				
				# second level remap method 1 (array swizzle)
				#array_index_remapped = remap_params_bit[(word_index * PARAMS['chip_num'] + chip_index) * PARAMS['chip_num'] + bit_index]
				#error_info[1] = array_index_remapped % PARAMS['chip_num']
				#error_info[2] = array_index_remapped / PARAMS['chip_num']
				#chip_index_bit = error_info[1]
				#word_index_bit = error_info[2]

				# second level remap method 2 : just push 4 to left (bits)
				bit_index_origin = (word_index * PARAMS['chip_num'] + chip_index) * PARAMS['chip_num'] + bit_index
				bit_index_remapped = (bit_index_origin + 4) % 512
				byte_index_remapped = bit_index_remapped / PARAMS['chip_num']
				error_info[1] = byte_index_remapped % PARAMS['chip_num']
				error_info[2] = byte_index_remapped / PARAMS['chip_num']
				chip_index_bit = error_info[1]  
				word_index_bit = error_info[2]  
				
				# third level remap (remap row 1 more time)
				row_index_bit = error_info[0]
				error_info[0] = remap_params_row[row_index_bit * PARAMS['chip_num'] + chip_index_bit]



class ChunkList():
	def __init__(self, row_num, chunk_size):
		self.__row_num = row_num
		self.__chunk_size = chunk_size
		self.__chunk_list = []
		for _ in range(row_num / chunk_size + 1):
			self.__chunk_list.append(AddressChunk())

	def add_error(self, error_dict):
		for row_index, error_index in error_dict.iteritems():
			chunk_index = row_index / self.__chunk_size
			row_index = row_index % self.__chunk_size
			self.__chunk_list[chunk_index].add_error(row_index, error_index)

	def remap(self, mapper):
		# verify mapper
		'''
		if mapper.verify():
			for chunk in self.__chunk_list:
				chunk.remap(mapper.get_remap_params_row())
		else:
			raise Exception('mapper is not verified')
		'''
		# for test, enable remap without verification
		for chunk in self.__chunk_list:
			chunk.remap(mapper.get_remap_params_row())

	def remap_more(self, mapper, mapper_bit):
		# verify mapper
		'''
		if mapper.verify():
			for chunk in self.__chunk_list:
				chunk.remap(mapper.get_remap_params_row())
		else:
			raise Exception('mapper is not verified')
		'''
		# for test, enable remap without verification
		for chunk in self.__chunk_list:
			chunk.remap_more(mapper.get_remap_params_row(),mapper_bit.get_remap_params_row())

	def get_error_in_word_hist(self):
		error_hist = {}
		for chunk in self.__chunk_list:
			for error_num, freq in chunk.get_error_in_word_hist().iteritems():
				if error_hist.has_key(error_num):
					error_hist[error_num] += freq
				else:
					error_hist[error_num]  = freq
		return error_hist

	def get_double_error_in_word(self):
		error_list = []
		for chunk in self.__chunk_list:
			error_list.append(chunk.get_double_error_in_word())
		return error_list

	def get_double_error_in_byte(self):
		error_list = []
		for chunk in self.__chunk_list:
			error_list.append(chunk.get_double_error_in_byte())
		return error_list

	def get_remapped_error_in_word_hist(self):
		error_hist = {}
		for chunk in self.__chunk_list:
			for error_num, freq in chunk.get_remapped_error_in_word_hist().iteritems():
				if error_hist.has_key(error_num):
					error_hist[error_num] += freq
				else:
					error_hist[error_num]  = freq
		return error_hist

	def get_remapped_double_error_in_word(self):
		error_list = []
		for chunk in self.__chunk_list:
			error_list.append(chunk.get_remapped_double_error_in_word())
		return error_list

	def get_remapped_double_error_in_byte(self):
		error_list = []
		for chunk in self.__chunk_list:
			error_list.append(chunk.get_remapped_double_error_in_byte())
		return error_list