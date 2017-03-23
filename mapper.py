
# mapper class which im
class Mapper():
	def __init__(self, chip_num, chunk_size):
		self.__remap_params_row = []
		self.__chip_num = chip_num
		self.__chunk_size = chunk_size

	def set_params_from_csv(self, params_file):
		with open(params_file, 'rb') as file:
			lines = file.readlines()
			for line in lines:
				line = line.split(',')
				if len(line) == 1:
					line = line[0].split('\t')
				for param in line:
					self.__remap_params_row.append(int(param))
				#params_list = map(lambda x: int(x), line)
				#self.__remap_params_row.append(params_list)
		if len(self.__remap_params_row) != self.__chunk_size * self.__chip_num:
			raise Exception("csv file does not match with chunk size")

	def set_params_from_list(self, params_list):
		self.__remap_params_row = params_list

	def verify(self):
		neighbor_dict = {}
		# initialize neighbor_dict
		for row_index in range(self.__chunk_size):
			neighbor_dict[row_index] = []
		for index in range(len(self.__remap_params_row)):
			param = self.__remap_params_row[index]
			# append upper neighbor
			neighbor_dict[param].append(self.__remap_params_row[index-self.__chip_num])
			# append lower neighbor
			neighbor_dict[param].append(self.__remap_params_row[(index+self.__chip_num)-len(self.__remap_params_row)])

		for key, value in neighbor_dict.iteritems():
			value = set(value)
			if len(value) != (self.__chip_num * 2):
				return False

		return True

	def get_remap_params_row(self):
		return self.__remap_params_row