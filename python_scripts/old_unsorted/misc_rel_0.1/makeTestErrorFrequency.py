""" Create simulated reads with barcodes from a given id file, with information about
correct barcodes in the read headers for a posteriori verification of demultiplexing.
"""
import argparse
import random
import shutil


def chooseEvent(prop_inserts=1, prop_deletions=1, prop_modifications=18):
    total = prop_inserts + prop_deletions + prop_modifications
    p = random.randrange(0, total)

    if p <= prop_inserts:
        return 'i'

    elif prop_inserts < p <= (prop_inserts + prop_deletions):
        return 'd'

    else:
        return 'm'


def getRandomBase():
    bases = ['A', 'C', 'G', 'T']
    return random.choice(bases)


def messupBarcode(barcode, errorFreq, mutation_model=None):
    res = ''
    qual = ''

    eventList = dict()

    if mutation_model == None:
        mutation_model = (None,)

    for i in range(errorFreq):
        # Will this error hit the barcode?
        pos = random.randrange(0, 100)
        if pos < len(barcode):
            # Hit!
            event = chooseEvent(*mutation_model)
            eventList[pos] = event

    i = 0
    while i < len(barcode):
        if i in eventList:
            event = eventList[i]
            if event == 'i':
                res += getRandomBase()
                qual += '?'
                del eventList[i]

            elif event == 'm':
                res += getRandomBase()
                qual += '?'
                i += 1

            else:
                # Deletion!
                i += 1
        else:
            res += barcode[i]
            qual += 'F'
            i += 1

    return [res, qual]


def main(fastqFile, index, reads, errorFreq, mutation_model=None):
    ids = open(index, 'r')
    outF = open(fastqFile, 'w')

    for i in range(reads):
        index = ids.readline()
        if not index:
            ids.seek(0)
            index = ids.readline()

        # Get the barcode
        barcode, _, _ = index.rstrip().partition('\t')
        bQual = ''
        [barcode, bQual] = messupBarcode(barcode, errorFreq, mutation_model)

        # Print this within a fastq, pos 10
        entry = '@Test_string\t{}\n'.format(index.rstrip())
        read = ''
        qual = ''
        for i in range(10):
            read += getRandomBase()
            qual += 'F'

        read += barcode
        qual += bQual
        for i in range(10):
            read += getRandomBase()
            qual += 'F'

        read += index.rstrip().split('\t')[0]
        qual += '!' * len(index.rstrip().split('\t')[0])

        entry += read + '\n+\n' + qual + '\n'
        outF.write(entry)

    outF.close()
    shutil.copy(fastqFile, fastqFile + '_pair')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    'python makeTestErrorFrequency.py out_fw.fastq index.txt number_of_reads errorFreq'

    parser.add_argument("out_fw_fastq", \
                        help="Output fastq file with forward reads.")
    parser.add_argument("index_txt", \
                        help="ID file with barcodes.")
    parser.add_argument("number_of_reads", \
                        help="Number of reads to simulate.", type=int)
    parser.add_argument("errorFreq", \
                        help="Frequency of errors in simulated reads (percentage)", \
                        type=int)
    parser.add_argument("-m", "--mutation_model", nargs="+", default=None, type=int, \
                        help="Model for mutation events, input as three integers, given "\
                             "as an 'inserts deletions modifications' triple. Then e.g. " \
                             "the proportion of inserts will be inserts / (inserts + " \
                             "deletions + modifications). Default values are '1 1 18'.")

    args = parser.parse_args()

    main(args.out_fw_fastq, args.index_txt, args.number_of_reads, \
         args.errorFreq, args.mutation_model)
