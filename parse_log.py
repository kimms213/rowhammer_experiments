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
	mapper_bit = Mapper(PARAMS['chip_num'], PARAMS['chunk_size'])
	mapper.set_params_from_csv('mapping_files/proposed_64_12.map')
	mapper_bit.set_params_from_csv('mapping_files/proposed_64_12.map')
	print mapper.verify()

	# remap every chunk
	#chunk_list.remap(mapper)

	# remap every chunk for double or triple remapping (your choice!)
	chunk_list.remap_more(mapper, mapper_bit)
	'''
	same_count = 0
	# print double error
	for errors in chunk_list.get_double_error_in_byte():
		if len(errors) == 0:
			continue
		same_count += 1
		print errors
	print same_count
	print "-------------------------------------------"
	'''
	same_count = 0
	for errors in chunk_list.get_remapped_double_error_in_byte():
		if len(errors) == 0:
			continue
		same_count += 1
		print errors
	
	print same_count
	

	# get error histogram
	print "Proposed_64_12"
	print "Array : proposed_64_12"
	print "Chunk size : ",PARAMS["chunk_size"]
	#print "Row + Array swizzle"
	#print "Row + Array + Row swizzle"
	print "Samsung_2G_B"
	#print "Samsung2G_B"
	print chunk_list.get_error_in_word_hist()
	print chunk_list.get_remapped_error_in_word_hist()
	
