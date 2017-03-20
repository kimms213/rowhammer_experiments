import re

# import user modules
from utils import PARAMS, read_log
from address_chunk import AddressChunk, ChunkList
from mapper import Mapper


# main function
if __name__ == "__main__":
	# read log and create error_dict
	#error_dict = read_log('log_files/log_kingmax_2G_1600_modi_print_new_170315_2')
	error_dict = read_log('log_files/log_samsung_2G_1600_B_modi_print_new_170317_2')
	# get number of rows in log
	max_row_num = max(error_dict.keys())
	print max_row_num
	# create ChunkList
	chunk_list = ChunkList(max_row_num, PARAMS['chunk_size'])
	# add error info to chunk_list
	chunk_list.add_error(error_dict)

	# create mapper
	mapper = Mapper(PARAMS['chip_num'], PARAMS['chunk_size'])
	mapper.set_params_from_csv('mapping_files/patent.map')
	print mapper.verify()

	# remap every chunk
	chunk_list.remap(mapper)

	# print double error
	for errors in chunk_list.get_double_error_in_word():
		if len(errors) == 0:
			continue
		print errors

	print "-------------------------------------------"
	for errors in chunk_list.get_remapped_double_error_in_word():
		if len(errors) == 0:
			continue
		print errors

	# get error histogram
	print "Patent"
	#print "proposed_ver7"
	#print "Array Swizzle"
	print "Samsung_B"
	#print chunk_list.get_error_in_word_hist()
	#print chunk_list.get_remapped_error_in_word_hist()
	
