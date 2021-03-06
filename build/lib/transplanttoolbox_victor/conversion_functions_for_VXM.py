#! usr/bin/python 

from __future__ import division, print_function, absolute_import
import argparse
import sys
import logging

import os
import re
import requests   
import operator
import glob
import transplanttoolbox_victor.vxm_hla
from transplanttoolbox_victor.vxm_hla import allele_truncate, locus_string_geno_list, expand_ac, single_locus_allele_codes_genotype


from transplanttoolbox_victor import __version__

__author__ = "Gragert Lab"
__copyright__ = "Gragert Lab"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)


allele_to_ag_dict = {}
population_allele_frequencies = {}
allele_frequencies = {}
b_bw_dict = {}
bw4_list = []
bw6_list = []


unosEQags = []
agbw46 = {}
### Dictionary with alleles and equivalent antigens


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNOS_conversion_table_filename = os.path.join(BASE_DIR,"transplanttoolbox_victor/UNOS_conversion_table_with_rules.csv")
UNOS_conversion_table_file = open(UNOS_conversion_table_filename, 'r')
for row in UNOS_conversion_table_file:
	expression_character = ""
	if row.startswith("Allele"):
		continue 
	else:
		allele = row.split(',')[0]
		allele_4d = transplanttoolbox_victor.vxm_hla.allele_truncate(allele)
		antigen = row.split(',')[1]
		unosEQags.append(antigen)
		rule = row.split(',') [2]
		bw4_6 = row.split(',')[3]
		if bw4_6 != "NA":
			agbw46[antigen] = bw4_6
		if bw4_6 == "Bw4":
			bw4_list.append(antigen)
		if bw4_6 == "Bw6":
			bw6_list.append(antigen)

		
		
	allele_to_ag_dict[allele] = antigen, rule, bw4_6 
	allele_to_ag_dict[allele_4d] = antigen, rule, bw4_6

bw4_list = list(set(bw4_list))
bw6_list = list(set(bw6_list))

unosagslist = list(set(unosEQags))

#print(unosagslist)
#print(len(unosagslist))

b_bw_dict["Bw4"] = bw4_list
b_bw_dict["Bw6"] = bw6_list

#print(agbw46)

race_list = ["AAFA", "AFA", "CAU", "HIS", "NAM", "AFB", "AINDI", "API",
			 "AISC", "ALANAM", "AMIND", "CARB", "CARHIS", "CARIBI", 
			"EURCAU", "FILII", "HAWI", "JAPI", "KORI", "MENAFC", "MSWHIS", "NCHI", "SCAHIS", "SCAMB", "SCSEAI", "VIET"] 

#print(b_bw_dict)	

for pop in race_list:
	file = BASE_DIR + "/transplanttoolbox_victor/freqs_6loc/" + pop + ".ARS.freqs"
	freq_file = open(file, 'r')
	for line in freq_file:
		if line.startswith("Haplo"):
			continue
		else:
			line_split = line.split(",")
			allele_list = line_split[0]
			count = line_split[1]
			haplotype_frequency = line_split[2]
			allele_split = allele_list.split("~")

			for allele in allele_split:
				allele = allele.rstrip("g")
				key = pop + "%" + allele
				if key in population_allele_frequencies:
					population_allele_frequencies[key] += float(haplotype_frequency)
				else:
					population_allele_frequencies[key] = float(haplotype_frequency)



#print(population_allele_frequencies)
def convert_allele_list_to_ags(hla_allele_list):
	
	"""This function can be called if a list of alleles has to be converted to antigens. Input format is a list and 
	the corresponding antigens and rules will be printed out"""
	allele_list_dict = {}
	ag_list = []
	bw4_6_list = []
	for allele in hla_allele_list:
		allele = allele.rstrip("p P g G")
		if allele in allele_to_ag_dict:
			ag = allele_to_ag_dict[allele][0]
			ag_list.append(ag)
			bw4_6 = allele_to_ag_dict[allele][2]
			if bw4_6 != "NA":
				bw4_6_list.append(bw4_6)
			
		else:
			continue
	
	bw46_list = list(set(bw4_6_list))
	ags = ag_list + bw46_list
				
	return ags

def gl_string_ags(gl_string, pop):
	gl_dict = {}
	gl_string = gl_string.replace("HLA-", "")
	locus_split = gl_string.split("^")

	ag_freq_1 = 0.0
	ag_freq_2 = 0.0
	geno_antigen_freq = {}

	ag_list = ""

	One_locus_typing = 0
	Two_locus_typing = 0
	Three_locus_typing = 0
	Four_locus_typing = 0
	Five_locus_typing = 0
	Six_locus_typing = 0

	

	if len(locus_split) == 1:
		One_locus_typing = 1
		print("One locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		ag_list = a_ags  




	if len(locus_split) == 2:
		Two_locus_typing = 1
		print("Two locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		geno_antigen_freq = {}
		b_locus = locus_split[1]
		b_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(b_locus)
		b_ags = genotype_ags(b_genotype_list,pop)
		ag_list = a_ags  + b_ags 




	if len(locus_split) == 3:
		Three_locus_typing = 1
		print("Three locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		geno_antigen_freq = {}
		b_locus = locus_split[1]
		b_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(b_locus)
		b_ags = genotype_ags(b_genotype_list,pop)
		geno_antigen_freq = {}
		c_locus = locus_split[2]
		c_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(c_locus)
		c_ags = genotype_ags(c_genotype_list,pop)
		ag_list = a_ags  + b_ags + c_ags
	
	
	if len(locus_split) == 4:
		Four_locus_typing = 1
		print("Four locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		geno_antigen_freq = {}
		b_locus = locus_split[1]
		b_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(b_locus)
		b_ags = genotype_ags(b_genotype_list,pop)
		geno_antigen_freq = {}
		c_locus = locus_split[2]
		c_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(c_locus)
		c_ags = genotype_ags(c_genotype_list,pop)
		geno_antigen_freq = {}
		dr_locus = locus_split[3]
		dr_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dr_locus)
		dr_ags = genotype_ags(dr_genotype_list,pop)
		ag_list = a_ags  + b_ags  + c_ags  + dr_ags

	if len(locus_split) == 5:
		Five_locus_typing = 1
		print("Five locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		geno_antigen_freq = {}
		b_locus = locus_split[1]
		b_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(b_locus)
		b_ags = genotype_ags(b_genotype_list,pop)
		geno_antigen_freq = {}
		c_locus = locus_split[2]
		c_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(c_locus)
		c_ags = genotype_ags(c_genotype_list,pop)
		geno_antigen_freq = {}
		dr_locus = locus_split[3]
		dr_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dr_locus)
		dr_ags = genotype_ags(dr_genotype_list,pop)
		geno_antigen_freq = {}
		dqb_locus = locus_split[4]
		dqb_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dqb_locus)
		dqb_ags = genotype_ags(dqb_genotype_list,pop)
		ag_list = a_ags  + b_ags  + c_ags   + dr_ags  + dqb_ags

	

	if len(locus_split) == 6:
		Six_locus_typing = 1
		print("Six locus typing")
		geno_antigen_freq = {}
		a_locus = locus_split[0]
		a_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(a_locus)
		a_ags = genotype_ags(a_genotype_list,pop)
		geno_antigen_freq = {}
		b_locus = locus_split[1]
		b_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(b_locus)
		b_ags = genotype_ags(b_genotype_list,pop)
		geno_antigen_freq = {}
		c_locus = locus_split[2]
		c_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(c_locus)
		c_ags = genotype_ags(c_genotype_list,pop)
		geno_antigen_freq = {}
		dr_locus = locus_split[3]
		dr_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dr_locus)
		dr_ags = genotype_ags(dr_genotype_list,pop)
		geno_antigen_freq = {}
		dqb_locus = locus_split[4]
		dqb_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dqb_locus)
		dqb_ags = genotype_ags(dqb_genotype_list,pop)
		geno_antigen_freq = {}
		dr345_locus = locus_split[5]
		dr345_genotype_list = transplanttoolbox_victor.vxm_hla.locus_string_geno_list(dr345_locus)
		dr345_ags = genotype_ags(dr345_genotype_list,pop)
		ag_list = a_ags + "," + b_ags + "," + c_ags  + "," + dr_ags + "," + dqb_ags + "," + dr345_ags
	#print(ag_list)
	#ages = ag_list[0::3]
	#bw46_list = ag_list[1::3]
	#probs = ag_list[2::3]
	#gl_dict = {"GL_string" : gl_string, "UNOS antigens": ages, "Bw4/6 epitopes": bw46_list, "Antigen Probablities": probs }
	#print(ag_list)
	return ag_list

	
def genotype_ags(genotype_list, pop):
	ag_freq_1 = 0.0
	ag_freq_2 = 0.0
	
	geno_antigen_freq = {}
	for genotype in genotype_list:
		allele_1 = genotype.split("+")[0]
		allele_1 = allele_1.rstrip("g p P G")
		allele_1 = transplanttoolbox_victor.vxm_hla.allele_truncate(allele_1)
		allele_pop1 = pop + "%" + allele_1


		allele_2 = genotype.split("+")[1]
		allele_2 = allele_2.rstrip("g p P G")
		allele_2 = transplanttoolbox_victor.vxm_hla.allele_truncate(allele_2)
		allele_pop2 = pop + "%" + allele_2

		ag_1 = allele_to_ag_dict[allele_1][0]
		bw46_1 = allele_to_ag_dict[allele_1][2]
		ag_2 = allele_to_ag_dict[allele_2][0]
		bw46_2 = allele_to_ag_dict[allele_2][2]
		


		if allele_1 in population_allele_frequencies:
			ag_freq_1 = population_allele_frequencies[allele_pop1]
		if allele_2 in population_allele_frequencies:
			ag_freq_2 = population_allele_frequencies[allele_pop2]

		gf = 0
		if (ag_1 == ag_2):
			gf = float(ag_freq_1) * float(ag_freq_2)
		else:
			gf = 2 * float(ag_freq_1) * float(ag_freq_2)	

		geno_antigen = ag_1 + "+" + ag_2
		
		if bw46_1 != "NA":

			geno_antigen = geno_antigen + "+" + bw46_1 

		if bw46_2	!= "NA":
			geno_antigen = geno_antigen + "+" + bw46_2	
			
		#print(geno_antigen)

		if geno_antigen in geno_antigen_freq.keys():
			geno_antigen_freq[geno_antigen] += float(gf)
		else:
			geno_antigen_freq[geno_antigen] = float(gf)

	TF = sum(geno_antigen_freq.values())
	if TF == 0.0:
		TF = 1
	else:
		TF = TF	

		
	for i,j in geno_antigen_freq.items():
		ag_probs = j/TF
		geno_antigen_freq[i] = round(ag_probs, 4)

		
	#print(geno_antigen_freq)		
	sorted_gf = sorted(geno_antigen_freq.items(), key = operator.itemgetter(1), reverse = True)
	#print(sorted_gf)
	#if len(sorted_gf) == 1:
		#ag_prob = 1
	#else:
		#antigen_list = sortef_gf[1::2]	
	#print(sorted_gf)
	# top_ag_geno = sorted_gf[0][0]
	# top_gf = sorted_gf[0][1]
	#print(top_ag_geno)	
	# ag_1 = top_ag_geno.split("+")[0]
	# ag_2 = top_ag_geno.split("+")[1]	
	#print(ag_1)
	#print(ag_2)
	# ag_list = ag_1 + "," + ag_2
	#bw46_list = bw46_1	+ "," + bw46_2
	return (sorted_gf)

def allele_freq(allele_list, pop):
	allele_pop_freqs = {}
	for i in allele_list:
		allele_pop_key = pop + "%" + i

		if allele_pop_key in population_allele_frequencies:
			allele_pop_freqs[i] = population_allele_frequencies[allele_pop_key]
		else: 
			allele_pop_freqs[i] = 0	

	return allele_pop_freqs	


def allele_code_ags(allele_codes_list, pop):

	ag_freq_1 = 0.0
	ag_freq_2 = 0.0
	geno_antigen_freq = {}
	ag_list = ""

	
	if len(allele_codes_list) == 2:
		print("One locus typing")
		One_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)
		ag_list = a_ags  


	if len(allele_codes_list) == 4:
		print("Two locus typing")
		Two_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)

		C_1_code = allele_codes_list[2]
		C_2_code = allele_codes_list[3]
		C_codes_pair = [C_1_code, C_2_code]
		geno_antigen_freq = {}
		ccodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(C_codes_pair)
		c_ags = genotype_ags(ccodes_genotype, pop)

		ag_list = a_ags  + c_ags  




	if len(allele_codes_list) == 6:
		print("Three locus typing")
		Three_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)

		C_1_code = allele_codes_list[2]
		C_2_code = allele_codes_list[3]
		C_codes_pair = [C_1_code, C_2_code]
		geno_antigen_freq = {}
		ccodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(C_codes_pair)
		c_ags = genotype_ags(ccodes_genotype, pop)

		B_1_code = allele_codes_list[4]
		B_2_code = allele_codes_list[5]
		B_codes_pair = [B_1_code, B_2_code]
		geno_antigen_freq = {}
		bcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(B_codes_pair)
		b_ags = genotype_ags(bcodes_genotype, pop)
		
		ag_list = a_ags  + b_ags  + c_ags

	if len(allele_codes_list) == 8:
		print("Four locus typing")
		Four_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)

		C_1_code = allele_codes_list[2]
		C_2_code = allele_codes_list[3]
		C_codes_pair = [C_1_code, C_2_code]
		geno_antigen_freq = {}
		ccodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(C_codes_pair)
		b_ags = genotype_ags(ccodes_genotype, pop)

		B_1_code = allele_codes_list[4]
		B_2_code = allele_codes_list[5]
		B_codes_pair = [B_1_code, B_2_code]
		geno_antigen_freq = {}
		bcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(B_codes_pair)
		c_ags = genotype_ags(bcodes_genotype, pop)
			
		dr_1_code = allele_codes_list[6]
		dr_2_code = allele_codes_list[7]
		dr_codes_pair = [dr_1_code, dr_2_code]
		geno_antigen_freq = {}
		drcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dr_codes_pair)
		dr_ags = genotype_ags(drcodes_genotype, pop)

		ag_list = a_ags  + b_ags + c_ags  + dr_ags
	
	if len(allele_codes_list) == 10:
		print("Five locus typing")
		Five_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)

		C_1_code = allele_codes_list[2]
		C_2_code = allele_codes_list[3]
		C_codes_pair = [C_1_code, C_2_code]
		geno_antigen_freq = {}
		ccodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(C_codes_pair)
		c_ags = genotype_ags(ccodes_genotype, pop)

		B_1_code = allele_codes_list[4]
		B_2_code = allele_codes_list[5]
		B_codes_pair = [B_1_code, B_2_code]
		geno_antigen_freq = {}
		bcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(B_codes_pair)
		b_ags = genotype_ags(bcodes_genotype, pop)
			
		dr_1_code = allele_codes_list[6]
		dr_2_code = allele_codes_list[7]
		dr_codes_pair = [dr_1_code, dr_2_code]
		geno_antigen_freq = {}
		drcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dr_codes_pair)
		dr_ags = genotype_ags(drcodes_genotype, pop)	
		
		dqb_1_code = allele_codes_list[8]
		dqb_2_code = allele_codes_list[9]
		dqb_codes_pair = [dqb_1_code, dqb_2_code]
		geno_antigen_freq = {}
		dqbcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dqb_codes_pair)
		dqb_ags = genotype_ags(dqbcodes_genotype, pop)

		ag_list = a_ags  + b_ags  + c_ags + dr_ags  + dqb_ags
				
	if len(allele_codes_list) == 12:
		print("Six locus typing")
		Six_locus_typing = 1
		A_1_code = allele_codes_list[0]
		A_2_code = allele_codes_list[1]
		A_codes_pair = [A_1_code, A_2_code]
		geno_antigen_freq = {}
		acodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(A_codes_pair)
		a_ags = genotype_ags(acodes_genotype, pop)

		C_1_code = allele_codes_list[2]
		C_2_code = allele_codes_list[3]
		C_codes_pair = [C_1_code, C_2_code]
		geno_antigen_freq = {}
		ccodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(C_codes_pair)
		c_ags = genotype_ags(ccodes_genotype, pop)

		B_1_code = allele_codes_list[4]
		B_2_code = allele_codes_list[5]
		B_codes_pair = [B_1_code, B_2_code]
		geno_antigen_freq = {}
		bcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(B_codes_pair)
		b_ags = genotype_ags(bcodes_genotype, pop)
			
		dr_1_code = allele_codes_list[6]
		dr_2_code = allele_codes_list[7]
		dr_codes_pair = [dr_1_code, dr_2_code]
		geno_antigen_freq = {}
		drcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dr_codes_pair)
		dr_ags = genotype_ags(drcodes_genotype, pop)	
		
		dqb_1_code = allele_codes_list[8]
		dqb_2_code = allele_codes_list[9]
		dqb_codes_pair = [dqb_1_code, dqb_2_code]
		geno_antigen_freq = {}
		dqbcodes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dqb_codes_pair)
		dqb_ags = genotype_ags(dqbcodes_genotype, pop)
							

		dr345_1_code = allele_codes_list[10]
		dr345_2_code = allele_codes_list[11]
		dr345_codes_pair = [dr345_1_code, dr345_2_code]
		geno_antigen_freq = {}
		dr345codes_genotype = transplanttoolbox_victor.vxm_hla.single_locus_allele_codes_genotype(dr345_codes_pair)
		dr345_ags = genotype_ags(dr345codes_genotype, pop)			


		ag_list = a_ags  + b_ags  + c_ags  + dr_ags  + dqb_ags  + dr345_ags


	#ages = ag_list[0::3]
	#bw46_list = ag_list[1::3]
	#probs = ag_list[2::3]
	#al_dict = {"Allele Codes" : allele_codes_list, "Antigens": ages, "Bw4/6 epitopes": bw46_list, "Antigen Probablities": probs}
	print(ag_list)
	return ag_list
	

def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Just a Fibonnaci demonstration")
    parser.add_argument(
        '--version',
        action='version',
        version='allan {ver}'.format(ver=__version__))
    parser.add_argument(
        dest="n",
        help="n-th Fibonacci number",
        type=int,
        metavar="INT")
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
    



