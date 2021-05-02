#!/usr/bin/env python3

import json
import argparse
import os

from standards.utils.json_handler import IntegerEncoder
from standards.utils.utils import increment_seed

RESULTS_DIR = 'results'


def seed_order(files, standard):
    if standard == 'x962':
        return sorted(files, key=lambda x: int((x.split(".")[-2]).split("_")[-1], 16), reverse=True)
    return sorted(files, key=lambda x: int((x.split(".")[-2]).split("_")[-1], 16))


def seed_update(seed, offset, standard):
    if standard == 'x962':
        return increment_seed(seed, -offset)
    return increment_seed(seed, offset)


def save_into_file(merged_name, merged, results_path):
    """save the merged results into a temp file, then delete all others, then rename it"""
    merged_name_tmp = f'{merged_name}.tmp'
    with open(merged_name_tmp, "w+") as fh:
        json.dump(merged, fh, cls=IntegerEncoder)

    for root, _, files in os.walk(results_path):
        for file in sorted(files, reverse=True):
            fname = os.path.join(root, file)
            if os.path.splitext(fname)[1] != ".tmp":
                os.remove(fname)
    os.rename(merged_name_tmp, merged_name)


def get_results(fname, merged, original_seed, standard, verbose=False):
    f = open(fname, "r")
    results = json.load(f)
    if verbose:
        print("Merging ", fname, "...")
    expected_initial_seed = seed_update(original_seed, merged["seeds_tried"], standard)

    if merged['seeds_tried'] == 0:
        merged.update(results)
    else:
        merged["curves"] += results["curves"]
        merged["seeds_tried"] += results["seeds_tried"]
        merged["seeds_successful"] += results["seeds_successful"]
    f.close()
    try:
        assert expected_initial_seed == results["initial_seed"]
    except AssertionError:
        raise ValueError(
            "The expected initial seed is ",
            expected_initial_seed,
            " but the current one is ",
            results["initial_seed"],
        )


def merge(standard, verbose=False):
    parameter_path = os.path.join('standards','parameters', f'parameters_{standard}.json')
    results_dir = os.path.join(RESULTS_DIR, standard)

    # get the names of immediate subdirs, which should be the respective bitsizes
    bitsizes = [f.name for f in os.scandir(results_dir) if f.is_dir()]

    for bitsize in bitsizes:
        results_path = os.path.join(results_dir, bitsize)

        # skip empty directories
        if len(os.listdir(results_path)) == 0:
            continue

        # get starting seed
        with open(parameter_path, "r") as f:
            params = json.load(f)
            original_seed = params[bitsize][1]

        merged = {"seeds_tried": 0}
        for root, _, files in os.walk(results_path):
            for file in seed_order(files, standard):
                get_results(os.path.join(root, file), merged, original_seed, standard, verbose)

        merged_name = os.path.join(results_path, f'{str(merged["seeds_tried"])}_{str(bitsize)}_{original_seed}.json')
        save_into_file(merged_name, merged, results_path)


def main():
    parser = argparse.ArgumentParser(description="Merge results")
    parser.add_argument('-s', "--standard", type=str, default='all', help="standards whose results should be merged")
    parser.add_argument('-v', "--verbose", action='store_true', help="")
    args = parser.parse_args()
    stds = args.standard
    if stds != 'all':
        merge(stds, args.verbose)
        return
    for f in os.scandir(RESULTS_DIR):
        if f.is_dir():
            merge(f.name, args.verbose)


if __name__ == '__main__':
    main()
