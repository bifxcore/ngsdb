#/usr/bin/python
__author__ = 'mcobb'

import sys
import os.path


def main():
	# Reads the file in from the command line. First file is the script, second is the vcf file,
	# and an option second is the summary file.
	num_of_files = len(sys.argv[1:])
	vcf_path = sys.argv[1]
	output = sys.argv[2]


	# If only a vcf file. Will be adjusted to automatically no through the command line input.
	if num_of_files == 2:
		#opens merge file (input)
		vcf_file = open(vcf_path, 'r')

		#creates and opens output file.
		new_file = open(output, 'wb')
		print "Results found at: ", output

		#loops through each line of the merge file
		for x in vcf_file:

			# if the line starts with Ld and is therefore a snp entry
			if x.startswith("Ld"):

				#Collects current statistics of each snp
				snp = x.split()
				ref = snp[3]
				alt = snp[4]
				info = snp[7].split(';')

				#Collets current statistics of each sample
				samples = snp[9:]
				num_samples = len(samples)


				#collects each statistic
				ACs_index = [i for i, s in enumerate(info) if s.startswith('AC=')]
				ACs = info[ACs_index[0]]

				AFs_index = [i for i, s in enumerate(info) if s.startswith('AF=')]
				AFs = info[AFs_index[0]]

				MLEACs_index = [i for i, s in enumerate(info) if s.startswith('MLEAC=')]
				MLEACs = info[MLEACs_index[0]]

				MLEAFs_index = [i for i, s in enumerate(info) if s.startswith('MLEAF=')]
				MLEAFs = info[MLEAFs_index[0]]

				#checks if reference alleles are multi-allelic
				if ',' in ref:
					alleles = ref.split(',')
					AC = ACs.replace('AC=', '').split(',')
					AF = AFs.replace('AF=', '').split(',')
					MLEAC = MLEACs.replace('MLEAC=', '').split(',')
					MLEAF = MLEAFs.replace('MLEAF=', '').split(',')

					size = len(alleles)
					for z in range(0, num_samples):
						new_samples = []
						for each in samples:
							if each == '.':
								each = '0/0:99:56:0,1992,1992:100,0'
							else:
								curr_samp = each.split(':')
								pl = curr_samp[3].split(',')
								pl[3] = pl[0]
								pl_groups = [",".join(pl[y:y+3]) for y in range(0, len(pl), 3)]
								for alle in range(0, size):
									curr_samp[3] = pl_groups[alle]

									gt = pl_groups[alle].split(',')
									gt_index = gt.index(min(gt))

							if gt_index == 0:
								new_gt = '0/0'
							elif gt_index == 1:
								new_gt = '0/1'
							elif gt_index == 2:
								new_gt = '1/1'
							else:
								pass
							curr_samp[0] = new_gt
							new_samp = ':'.join(curr_samp)
							new_samples.append(new_samp)

						snp[9:] = new_samples
					for i in range(0, size):
						try:
							new_ac = 'AC=' + AC[i]
						except IndexError:
							new_ac = 'AC=' + AC[0]
						try:
							new_af = 'AF=' + AF[i]
						except IndexError:
							new_ac = 'AF=' + AF[0]
						try:
							new_mleac = 'MLEAC=' + MLEAC[i]
						except IndexError:
							new_ac = 'MLEAC=' + MLEAC[0]
						try:
							new_mleaf = 'MLEAF=' + MLEAF[i]
						except IndexError:
							new_ac = 'MLEAF=' + MLEAF[0]

						info[ACs_index[0]] = new_ac
						info[AFs_index[0]] = new_af
						info[MLEACs_index[0]] = new_mleac
						info[MLEAFs_index[0]] = new_mleaf

						new_info = ';'.join(info)

						snp[3] = alleles[i]
						snp[7] = new_info

						line = '\t'.join(snp)
						new_file.write(line + "\n")


				#checks if alternate alleles are multi-allelic
				elif ',' in alt:
					alleles = alt.split(',')
					AC = ACs.replace('AC=', '').split(',')
					AF = AFs.replace('AF=', '').split(',')
					MLEAC = MLEACs.replace('MLEAC=', '').split(',')
					MLEAF = MLEAFs.replace('MLEAF=', '').split(',')

					size = len(alleles)
					for z in range(0, num_samples):
						new_samples = []
						for each in samples:
							if each == '.':
								each = '0/0:99:56:0,1992,1992:100,0'
							else:
								curr_samp = each.split(':')
								pl = curr_samp[3].split(',')
								pl[3] = pl[0]
								pl_groups = [",".join(pl[y:y+3]) for y in range(0, len(pl), 3)]
								for alle in range(0, size):
									curr_samp[3] = pl_groups[alle]

									gt = pl_groups[alle].split(',')
									gt_index = gt.index(min(gt))

							if gt_index == 0:
								new_gt = '0/0'
							elif gt_index == 1:
								new_gt = '0/1'
							elif gt_index == 2:
								new_gt = '1/1'
							else:
								pass
							curr_samp[0] = new_gt
							new_samp = ':'.join(curr_samp)
							new_samples.append(new_samp)

						snp[9:] = new_samples
					for i in range(0, size):
						try:
							new_ac = 'AC=' + AC[i]
						except IndexError:
							new_ac = 'AC=' + AC[0]
						try:
							new_af = 'AF=' + AF[i]
						except IndexError:
							new_ac = 'AF=' + AF[0]
						try:
							new_mleac = 'MLEAC=' + MLEAC[i]
						except IndexError:
							new_ac = 'MLEAC=' + MLEAC[0]
						try:
							new_mleaf = 'MLEAF=' + MLEAF[i]
						except IndexError:
							new_ac = 'MLEAF=' + MLEAF[0]

						info[ACs_index[0]] = new_ac
						info[AFs_index[0]] = new_af
						info[MLEACs_index[0]] = new_mleac
						info[MLEAFs_index[0]] = new_mleaf

						new_info = ';'.join(info)

						snp[4] = alleles[i]
						snp[7] = new_info

						line = '\t'.join(snp)
						new_file.write(line + "\n")

				else:
					line = '\t'.join(snp)
					new_file.write(line + "\n")
					pass
			else:
				new_file.write(x)
				pass
		new_file.close()
		vcf_file.close()

	elif num_of_files == 1:
		print "Need a vcf file and output file"
	else:
		print "Need a vcf file to split and an output file."


main()
