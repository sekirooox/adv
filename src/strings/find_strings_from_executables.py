import argparse
from src.pe_modifier import PEModifier
import os
import re
import json
import random

"""提取strings信息到JSON文件中"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find strings from executables')
    parser.add_argument("--executables_filepath",
                        type=str,
                        help="Filepath of the executables",
                        default='../../raw/BODMAS/benign'
                        )
    parser.add_argument("--output_filepath",
                        type=str,
                        help="Output file containing the strings found",
                        default='../../raw/strings.json'# 需要制定为json文件
                        )
    parser.add_argument("--min_length",
                        type=int,
                        default=5,
                        help="Minimum length of the string")
    parser.add_argument("--num_samples",
                        type=int,
                        default=300,
                        help="Num samples")
    parser.add_argument("--K",# 提取字符串的数量，没有设置则默认提取所有字符串
                        type=int,
                        default=None,
                        help="Default number of strings to consider")
    args = parser.parse_args()

    if args.min_length == 5:
        allstrings = re.compile(b'[\x20-\x7f]{5,}')
    elif args.min_length == 8:
        allstrings = re.compile(b'[\x20-\x7f]{8,}')
    elif args.min_length == 10:
        allstrings = re.compile(b'[\x20-\x7f]{10,}')

    filenames = os.listdir(args.executables_filepath)
    random.shuffle(filenames)
    total_strings = 0

    strings_dictionary = {}
    encoding = 'utf-8'
    for i, filename in enumerate(filenames[:args.num_samples]):
        print("{};{}".format(i, filename))
        try:
            pe_modifier = PEModifier(os.path.join(args.executables_filepath, filename))
            if pe_modifier.lief_binary is None:
                print("Exception loading binary!")
            else:
                executable_strings = allstrings.findall(pe_modifier.bytez)
                total_strings += len(executable_strings)
                for string in executable_strings:
                    try:
                        strings_dictionary[str(string, encoding)] += 1
                    except KeyError:
                        strings_dictionary[str(string, encoding)] = 1
        except Exception as e:
            print(e)
        print("Total strings: {}".format(total_strings))
    sort_strings_dictionary = sorted(strings_dictionary.items(), key=lambda x: x[1], reverse=True)
print('现在开始存储文件！')
try:
    if args.K is not None:
        with open(args.output_filepath, "w") as output_file:
            json.dump(sort_strings_dictionary[:args.K], output_file)
    else:
        with open(args.output_filepath, "w") as output_file:
            json.dump(sort_strings_dictionary, output_file)
except Exception as e:
    print(f"Error writing to file: {e}")
print('文件存储完成！')

