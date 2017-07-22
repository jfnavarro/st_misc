""" Compare kmer profiles of genomes for given k
"""
import argparse
from st_toolbox.data import readfq


def report(fh, k, numbers):
    """ Write some intermediate stats in a file
    """
    fmt = '\nTotal genome bases read: {nbases}\n' \
    'Unique ribo {k}mers: {ribo}\n' \
    'Unique genome {k}mers: {gnom}\n' \
    'Overlapping {k}mers: {overlap}\n\n'

    txt = fmt.format(k=k, nbases=numbers[0], ribo=numbers[1], gnom=numbers[2], overlap=numbers[3])
    fh.write(txt)


def main(args):
    out = open("gkc.out", "w")
    print('Will compare {}mers between {} and {}'.format(args.k, args.ribo, args.genome))
    out.write('Will compare {}mers between {} and {}'.format(args.k, args.ribo, args.genome))
    out.flush()
    k = args.k
    with open(args.ribo) as fh:
        fa = readfq(fh)
        ribos = [t[1] for t in fa]

    ribo_kmers = set()
    for ribo in ribos:
        ribo_kmers |= set(str(ribo[i:i + k]) for i in xrange(len(ribo) - k))

    genome_kmers = set()
    append_fmt = '{}{}'
    fh = open(args.genome)
    num_bases = 0
    try:
        for i, line in enumerate(fh):
            if line[0] == '>':
                from_prev = ''
                continue

            seq_part = append_fmt.format(from_prev, line)
            part_kmers = set(seq_part[i:i + k] for i in xrange(len(seq_part) - k))
            genome_kmers |= part_kmers
            num_bases += len(line)
            from_prev = line[-k:]

            # This should report ~20 times through the iteration
            # (based on a genome size of ~3.5 gigabases)
            if i % 2187500 == 0:
                num_ribo_kmers = len(ribo_kmers)
                num_genome_kmers = len(genome_kmers)
                overlap = len(ribo_kmers & genome_kmers)
                report(out, k, (num_bases, num_ribo_kmers, num_genome_kmers, overlap))

    finally:
        fh.close()

        num_ribo_kmers = len(ribo_kmers)
        num_genome_kmers = len(genome_kmers)
        overlap = len(ribo_kmers & genome_kmers)
        report(out, k, (num_bases, num_ribo_kmers, num_genome_kmers, overlap))
        out.close()

        print('\nTotal genome bases read: {}'.format(num_bases))
        print('Unique ribo {}mers: {}'.format(k, num_ribo_kmers))
        print('Unique genome {}mers: {}'.format(k, num_genome_kmers))
        print('Overlapping {}mers: {}'.format(k, overlap))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ribo', help='ribo fasta file')
    parser.add_argument('genome', help='genome fasta file')
    parser.add_argument('-k', help='kmer length', default=15, type=int)

    args = parser.parse_args()

    main(args)
