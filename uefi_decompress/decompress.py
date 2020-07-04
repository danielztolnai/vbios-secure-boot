#!/usr/bin/env python
import argparse
import EfiCompressor

def decompress_efi_rom(pe_img):
	pe_img = EfiCompressor.UefiDecompress(pe_img, len(pe_img))[:]
	return pe_img

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', type=argparse.FileType('rb'))
	parser.add_argument('outfile', type=argparse.FileType('wb'))
	args = parser.parse_args()

	o = args.outfile
	i = args.infile.read()
	o.write(decompress_efi_rom(i))
	o.close()
	args.infile.close()
