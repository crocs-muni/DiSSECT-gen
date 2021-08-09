#!/usr/bin/env python3

import json
import argparse
import os

from standards.utils import IntegerEncoder, seed_order, STANDARDS, seed_update

RESULTS_DIR = 'results'


def save_into_file(merged_name: str, merged: dict, results_path: str):
    """Save the merged results into a temp file, then delete all others, then rename it"""
    merged_name_tmp = f'{merged_name}.tmp'
    with open(merged_name_tmp, "w+") as fh:
        json.dump(merged, fh, cls=IntegerEncoder)

    for root, _, files in os.walk(results_path):
        for file in sorted(files, reverse=True):
            file_name = os.path.join(root, file)
            if os.path.splitext(file_name)[1] != ".tmp":
                os.remove(file_name)
    os.rename(merged_name_tmp, merged_name)


def merge_dictionaries(std, file_name: str, merged: dict, original_seed: str, verbose=False):
    """Merges dictionary from a file (file_name) with the rest of results in dictionary (merged)"""
    with open(file_name, "r") as f:
        results = json.load(f)
    if verbose:
        print("Merging ", file_name, "...")
    expected_initial_seed = seed_update(std, original_seed, merged["seeds_tried"])
    if merged['seeds_tried'] == 0:
        merged.update(results)
    else:
        merged["curves"] += results["curves"]
        merged["seeds_tried"] += results["seeds_tried"]
        merged["seeds_successful"] += results["seeds_successful"]
    assert expected_initial_seed == results[
        "initial_seed"], f"The expected seed is {expected_initial_seed}, the current one is {results['initial_seed']}"


def get_initial_seed(path, ordered_files):
    """Get the initial seed from a list of files ordered by seeds"""
    file_name = ordered_files[0]
    with open(os.path.join(path,file_name), "r") as f:
        results = json.load(f)
    return results['initial_seed']


def merge(std, path_to_results: str, verbose=False):
    """Merges results of the standard (std)"""
    bit_sizes = [f.name for f in os.scandir(path_to_results) if f.is_dir()]
    for bit_size in bit_sizes:
        results_path = os.path.join(path_to_results, bit_size)
        if len(os.listdir(results_path)) == 0:
            continue
        merged = {"seeds_tried": 0}
        root, _, files = list(os.walk(results_path))[0]
        ordered_files = seed_order(files)
        initial_seed = get_initial_seed(root, ordered_files)
        for file in ordered_files:
            merge_dictionaries(std, str(os.path.join(root, file)), merged, initial_seed, verbose)

        merged_name = os.path.join(results_path, f'{str(merged["seeds_tried"])}_{str(bit_size)}_{initial_seed}.json')
        save_into_file(merged_name, merged, results_path)


def main():
    parser = argparse.ArgumentParser(
        description="Did dissectgen created too much files for your taste? Use Merge results!")
    parser.add_argument('-s', "--standard", default='all', help="Standard whose results should be merged")
    parser.add_argument('-v', "--verbose", action='store_false', help="Verbosity of output")
    parser.add_argument('-r', "--results", action='store_true', default='.',
                        help=f"Path to the directory {RESULTS_DIR} with files containing results")

    args = parser.parse_args()
    path_to_results = os.path.join(args.results, RESULTS_DIR)
    if args.standard == 'all':
        stds = [f.name for f in os.scandir(path_to_results) if f.is_dir() and f.name in STANDARDS]
    else:
        stds = [args.standard]
    for std in stds:
        path_to_std = os.path.join(path_to_results, std)
        merge(std, path_to_std, verbose=args.verbose)


if __name__ == '__main__':
    main()
