import csv
import numpy as np
from copy import deepcopy
np.set_printoptions(threshold=np.inf)


if __name__ == "__main__":
	with open("error_test/chip_error.csv", "rb") as chip_error_file:
		chip_error_reader = csv.reader(chip_error_file, delimiter=',')
		chip_error_list = []
		for row in chip_error_reader:
			chip_error_list.append(row)
		chip_error_array = np.array(chip_error_list,dtype=float)


	with open("mapping_files/unit_mapping/unit_origin.map", 'rb') as file:
		lines = file.readlines()
		remap_params_list = []
		for line in lines:
			line = line.split(',')
			if len(line) == 1:
				line = line[0].split('\t')
			for param in line:
				remap_params_list.append(int(param))	
		remap_params_row = np.array(remap_params_list,dtype=int)


	remapped_chip_array = deepcopy(chip_error_array)
	sum_remap_chip_array = np.zeros((128),dtype=float)
	average_minus_sum_chip_array = np.zeros((128),dtype=float)

	for i in range(128):
		for j in range(8):
			remapped_chip_array[i][j] = chip_error_array[remap_params_row[8*i+j]][j]
			sum_remap_chip_array[i] += remapped_chip_array[i][j]
		average_minus_sum_chip_array[i] = sum_remap_chip_array[i]-5	
		# change 5 as total test results number 
		# now there are 5 test samples

	total_array_avg = np.zeros((128,9),dtype=float)
	
	for i in range(128):
		for j in range(8):
			total_array_avg[i][j] = remapped_chip_array[i][j]
		total_array_avg[i][8] = average_minus_sum_chip_array[i]

	print "Standard Deviation : ", np.std(average_minus_sum_chip_array)
	
	with open("error_test/remapped_unit_origin.csv", "wb") as file:
		writer = csv.writer(file, delimiter=',')
		for row in total_array_avg:
			writer.writerow(row)

	'''
	with open("error_test/remapped_unit_ver1", "wb") as file:
		writer = csv.writer(file, delimiter=',')
		for row in remapped_chip_array:
			writer.writerow(row)

	with open("error_test/remapped_unit_ver1.csv", "ab") as files:
		writer = csv.writer(files, delimiter=',')
		for row in average_remap_chip_array:
			writer.writerow(row)
	'''