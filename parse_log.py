import re

# import user modules
from utils import PARAMS, read_log
from address_chunk import AddressChunk, ChunkList
from mapper import Mapper


# main function
if __name__ == "__main__":
	# read log and create error_dict
	error_dict = read_log('log_files/log_samsung_2G_1600_A_modi_print_new_170313_test7 (6)')
	# get number of rows in log
	max_row_num = max(error_dict.keys())
	print max_row_num
	# create ChunkList
	chunk_list = ChunkList(max_row_num, PARAMS['chunk_size'])
	# add error info to chunk_list
	chunk_list.add_error(error_dict)

	# create mapper
	mapper = Mapper(PARAMS['chip_num'], PARAMS['chunk_size'])
	mapper.set_params_from_csv('mapping_files/proposed.map')
	print mapper.verify()

	# remap every chunk
	chunk_list.remap(mapper)

	# get error histogram
	print chunk_list.get_error_in_word_hist()
	print chunk_list.get_remapped_error_in_word_hist()