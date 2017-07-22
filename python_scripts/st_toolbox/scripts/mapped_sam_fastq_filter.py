""" Takes a sam file with the original (single end) fastq file and filters out
the reads from the original fastq file which are mapped.
"""
import argparse

from st_toolbox.data import readfq


def main(args):
    fq_format = '@{header}\n{sequence}\n+\n{quality}\n'

    mapped = set([])
    with open(args.sam) as fh:
        for line in fh:
            if line[0] == '@':
                continue

            row = line.split('\t')
            if row[2] != '*':
                mapped.add(row[0])

    in_fh = open(args.fastq)
    out_fh = open(args.out_fastq, 'w')

    reader = readfq(in_fh)
    for name, seq, qual in reader:
        if name in mapped:
            read = fq_format.format(header=name, sequence=seq, quality=qual)
            out_fh.write(read)

    in_fh.close()
    out_fh.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fastq', help='Original fastq file.')
    parser.add_argument('sam', help='Mapped sam file.')
    parser.add_argument('out_fastq', help='Name of filtered output fastq.')

    args = parser.parse_args()
    main(args)
