""" Generate outcome for findIndexWpairEnd for simulated reads of varying quality.
"""
import argparse
import subprocess
import os

import json


def output_to_dict(output):
    d = {}
    for l in output.split("\n"):
        k, _, v = l.partition(": ")
        try:
            d[k] = int(v)
        except ValueError:
            continue

    return d


def main(id_file, input_fastq, output_fastq, stats_file, k, m, l, \
         num_reads, tmp_dir, mutation_model):
    # findIndexesWpairEnd settings
    s = 10  # Hardcoded in makeTestErrorFrequency.py

    stats = []
    for err_freq in range(1, 51):
        stat = {"Error frequency": err_freq}
        stat["Settings"] = {"k": k, "m": m, "l": l}

        # Generate simulated fastq file
        mm = mutation_model
        subprocess.check_call(["makeTestErrorFrequency.py", \
                               input_fastq, id_file, str(num_reads), str(err_freq), \
                               "--mutation_model", str(mm[0]), str(mm[1]), str(mm[2])])

        # Map back reads with simulated errors
        findind_cl = ["findIndexWpairEnd", \
                      "-s", str(s), "-m", str(m), "-k", str(k), "-l", str(l), \
                      id_file, input_fastq, input_fastq + "_pair", \
                      output_fastq + "_pair", output_fastq, tmp_dir + "stats.txt"]
        try:
            output = subprocess.check_output(findind_cl)

        except subprocess.CalledProcessError:
            # Don't bother storing results if mapping failed
            continue

        stat["Results"] = output_to_dict(output)

        # Check for falsely mapped barcodes
        check_cl = ["checkResultIndexes.py", output_fastq, tmp_dir + "mismatches.txt"]
        output = subprocess.check_output(check_cl)

        stat["Check"] = output_to_dict(output)

        stats.append(stat)

    with open(stats_file, "w") as fh:
        json.dump(stats, fh, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("id_file", help="Path to id file to construct reads from.")
    parser.add_argument("output_stats", help="Output json file with gathered statistics.")

    parser.add_argument("-k", help="kmer length", type=int, default=2)
    parser.add_argument("-m", help="allowed mismatches per kmer", type=int, default=9)
    parser.add_argument("-l", help="barcode (id) length", type=int, default=27)

    parser.add_argument("--mutation_model", nargs="+", default=[1, 1, 18], type=int)

    args = parser.parse_args()

    id_file = args.id_file

    stats_file = args.output_stats

    with open(id_file) as fh:
        num_reads = sum(1 for line in fh)

    k = args.k
    m = args.m
    l = args.l

    tmp_dir = "tmp_k{}m{}l{}/".format(k, m, l)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    input_fastq = tmp_dir + "simulated.fastq"
    output_fastq = tmp_dir + "out.fastq"

    main(id_file, input_fastq, output_fastq, stats_file, k, m, l, \
         num_reads, tmp_dir, args.mutation_model)
