import numpy as np

def lsb(mid:int) -> int:
	pass

def msb(mid:int) -> int:
	pass

def hw(mid: list) -> int:
	'''
	## hamming weight leakage model

	`mid`: sensitive mid value.

	Returns:
		hw[value].
	>>> hw(3)=2
	'''
	return np.array([bin(iv).count("1") for iv in mid])