
# mapper class which im
class Mapper():
	def __init__(self, chip_num, chunk_size):
		self.__mapping_params = []
		self.__chip_num = chip_num
		self.__chunk_size = chunk_size

	def set_params_from_csv(self, params_file):
		with open(params_file, 'rb') as file:
			lines = file.readlines()
			for line in lines:
				line = line.split(',')
				for param in line:
					self.__mapping_params.append(int(param))
				#params_list = map(lambda x: int(x), line)
				#self.__mapping_params.append(params_list)

	def set_params_from_list(self, params_list):
		self.__mapping_params = params_list

	def verify(self):
		neighbor_dict = {}
		# initialize neighbor_dict
		for row_index in range(self.__chunk_size):
			neighbor_dict[row_index] = []
		for index in range(len(self.__mapping_params)):
			param = self.__mapping_params[index]
			# append upper neighbor
			neighbor_dict[param].append(self.__mapping_params[index-self.__chip_num])
			# append lower neighbor
			neighbor_dict[param].append(self.__mapping_params[(index+self.__chip_num)-len(self.__mapping_params)])

		for key, value in neighbor_dict.iteritems():
			value = set(value)
			if len(value) != (self.__chip_num * 2):
				return False

		return True

	def get_params(self):
		return self.__mapping_params