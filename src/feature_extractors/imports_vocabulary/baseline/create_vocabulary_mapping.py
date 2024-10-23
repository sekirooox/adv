# 原始代码
# import json
# from collections import OrderedDict
#
# with open("small_dll_imports.json", "r") as input_file:
#     data = json.load(input_file)
#
# vocabulary_mapping = OrderedDict()
# inverse_vocabulary_mapping = OrderedDict()
#
# i = 0
# for lib in data:
#     for function in data[lib]:
#         vocabulary_mapping["{};{}".format(lib.lower(), function)] = i
#         inverse_vocabulary_mapping[i] = "{};{}".format(lib.lower(), function)
#         i += 1
#
# with open("vocabulary/vocabulary_mapping.json", "w") as output_file:
#     json.dump(vocabulary_mapping, output_file)
#
# with open("vocabulary/inverse_vocabulary_mapping.json", "w") as output_file:
#     json.dump(inverse_vocabulary_mapping, output_file)
import json
from collections import OrderedDict
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create vocabulary mapping from small DLL imports JSON file')
    parser.add_argument("--input_filepath",
                        type=str,
                        help="Filepath of the input JSON file containing DLL imports",
                        default='../../../api_functions/count_functions_benign.json',
                        )
    parser.add_argument("--vocabulary_mapping_filepath",
                        type=str,
                        help="JSON-like file where the vocabulary mapping will be stored",
                        default="vocabulary/vocabulary_mapping_test.json")
    parser.add_argument("--inverse_vocabulary_mapping_filepath",
                        type=str,
                        help="JSON-like file where the inverse vocabulary mapping will be stored",
                        default="vocabulary/inverse_vocabulary_mapping_test.json")

    args = parser.parse_args()

    with open(args.input_filepath, "r") as input_file:
        data = json.load(input_file)

    vocabulary_mapping = OrderedDict()
    inverse_vocabulary_mapping = OrderedDict()

    i = 0
    for lib in data:
        for function in data[lib]:
            vocabulary_mapping["{};{}".format(lib.lower(), function)] = i
            inverse_vocabulary_mapping[i] = "{};{}".format(lib.lower(), function)
            i += 1

    with open(args.vocabulary_mapping_filepath, "w") as output_file:
        json.dump(vocabulary_mapping, output_file)

    with open(args.inverse_vocabulary_mapping_filepath, "w") as output_file:
        json.dump(inverse_vocabulary_mapping, output_file)
