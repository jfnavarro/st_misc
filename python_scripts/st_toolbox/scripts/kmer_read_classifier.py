""" Simply classify reads using kmer profiles
"""
import argparse
from collections import defaultdict
from itertools import tee, izip
import os
import sys

from st_toolbox.data import readfq


def prc_format(x, pos=0):
    return '{:.1%}'.format(x)


def histogram(args):
    """ Make a histogram over kmer overlaps for reads over reference, to
    evaluate a proper cutoff value.
    """
    import matplotlib.pylab as plt
    from matplotlib.ticker import FuncFormatter

    with open(args.reference) as fh:
        fa = readfq(fh)
        contams = [t[1] for t in fa]

    k = args.k

    kmers = set()
    for contam in contams:
        kmers |= set(str(contam[i:i + k]) for i in xrange(len(contam) - k))

    kmers = frozenset(kmers)

    fh = open(args.fastq)
    fq = readfq(fh)

    overlap = defaultdict(int)
    for _, seq, _ in fq:
        read_kmers = frozenset(seq[i:i + k] for i in xrange(len(seq) - k))
        overlap[round(100 * float(len(read_kmers.intersection(kmers))) / len(seq), 0)] += 1

    fh.close()

    out_file = os.path.basename(args.fastq).replace('.fastq', '_kmer_histogram.png')
    keys = sorted(overlap.keys())
    nreads = sum(overlap.values())
    percentages = [float(v) / nreads for v in overlap.values()]

    cumulative = [float(overlap[keys[0]]) / nreads]
    for key in keys[1:]:
        cumulative.append(cumulative[-1] + float(overlap[key]) / nreads)

    plt.bar(overlap.keys(), percentages, ec='none', label='histogram')
    plt.plot(keys, cumulative, label='cumulative')

    plt.gca().yaxis.set_major_formatter(FuncFormatter(prc_format))
    plt.grid(True)

    title = \
    """kmer overlap
    k = {}
    number of reads: {}"""

    plt.title(title.format(k, nreads))
    plt.xlabel('Overlapment')
    plt.ylabel('% of reads')
    plt.legend()

    plt.tight_layout()
    plt.savefig(out_file)


def split(args):
    """ Split the given fastq file to two different fastq files depending on
    the read being contaminated or not.
    """
    with open(args.reference) as fh:
        fa = readfq(fh)
        contams = [t[1] for t in fa]

    k = args.k
    cutoff = args.overlap_cutoff

    kmers = set()
    for contam in contams:
        kmers |= set(str(contam[i:i + k]) for i in xrange(len(contam) - k))

    kmers = frozenset(kmers)

    fh = open(args.fastq)
    fq = readfq(fh)

    fq_format = '@{header}\n{sequence}\n+\n{quality}\n'

    fname = os.path.basename(args.fastq)
    contam_fh = open(fname.replace('.fastq', '_contam.fastq'), 'w')
    clean_fh = open(fname.replace('.fastq', '_clean.fastq'), 'w')

    for head, seq, qual in fq:
        read_kmers = frozenset(seq[i:i + k] for i in xrange(len(seq) - k))

        overlapment = 100 * float(len(read_kmers.intersection(kmers))) / len(seq)
        if overlapment > cutoff:
            contam_fh.write(fq_format.format(header=head, sequence=seq, quality=qual))

        else:
            clean_fh.write(fq_format.format(header=head, sequence=seq, quality=qual))

    clean_fh.close()
    contam_fh.close()
    fh.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', help='reference fasta file')
    parser.add_argument('fastq', help='fastq file with reads to classify')
    parser.add_argument('--mode', help='script mode, either "histogram" or "split"', \
                        default='histogram')
    parser.add_argument('--k', help='kmer length, default 15', default=15, type=int)
    parser.add_argument('--overlap_cutoff', help='kmer overlap cutoff, default 20', \
                        default=20, type=int)

    args = parser.parse_args()

    if args.mode == 'histogram':
        histogram(args)

    elif args.mode == 'split':
        split(args)
