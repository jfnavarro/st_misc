""" Generate sbatch files for running mapping at different error rates,
for different settings of findIndexesWpairEnd.
"""
import argparse

sbatch_string = \
"""#!/bin/bash
#SBATCH -A b2011007
#SBATCH -p node
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -t 14:00:00
#SBATCH -J "err_rate_mapping_m{m}k{k}l{l}"
#SBATCH -D {out_directory}
#SBATCH --mail-user valentine.svensson@scilifelab.se
#SBATCH --mail-type=ALL

mapping_at_different_error_rates.py -m {m} -k {k} -l {l} {id_file} {out_file} --mutation_model 75 5 20
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("id_file", help="Path to id file to construct reads from.")
    parser.add_argument("l", help="Barcode (id) length.")
    parser.add_argument("out_directory", help="Output directory for sbatches to work in")

    args = parser.parse_args()

    l = args.l
    out_directory = args.out_directory
    id_file = args.id_file

    for k in range(5, 11):
        for m in range(2, min(k - 1, 8)):
            out_file = "mapping_results_stats_m{m}k{k}l{l}.json".format(m=m, k=k, l=l)
            sh_file = out_directory + "error_rate_mapping_m{m}k{k}l{l}.sh".format(m=m, k=k, l=l)
            with open(sh_file, "w") as fh:
                fh.write(sbatch_string.format(m=m, k=k, l=l, out_directory=out_directory, \
                                              id_file=id_file, out_file=out_file))
