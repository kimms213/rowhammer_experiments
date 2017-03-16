# PARAMETERS
PARAMS = {
	# DRAM parameters
	'chip_num'  : 8	,
	'capacity'  : 2 ** 34,
	'bank_num'  : 2 ** 3,
	'row_num'   : 2 ** 15,
	# unit paramaters 
	'unit_size' : 2 ** 9,
	# chunk parameters
	'chunk_size': 32
}

def unit_num_per_row(params):
	return params['capacity'] / (params['bank_num'] * params['row_num'] * params['unit_size'])

PARAMS['unit_num'] = unit_num_per_row(PARAMS)


import re
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