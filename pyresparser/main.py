import pandas as pd
import argparse
import glob
from pathlib import Path
from pyresparser import ResumeParser

arg_parser = argparse.ArgumentParser(prog="Pyresparser", description="Parsing resumes using pyresparser library")
arg_parser.add_argument("-id", "--input_dir", help="Input directory of resume files")
arg_parser.add_argument("-od", "--output_dir", help="Output directory of resume files")
arg_parser.add_argument("-e", "--exts", nargs='+', help="Extensions to parse. All if empty.")
args = arg_parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
exts = args.exts

if input_dir is None:
    arg_parser.print_help()
    raise Exception("Must specify input directory of the resumes")
if output_dir is None:
    arg_parser.print_help()
    raise Exception("Must specify output directory of the resumes")

input_files = glob.glob(input_dir + "/*")
input_files = list( filter(lambda f: Path(f).suffix in exts, input_files) ) \
    if len(exts) > 0 \
    else input_files

for input_file in input_files:
    data = ResumeParser(input_file).get_extracted_data()
    print(data)
