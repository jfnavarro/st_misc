#! /usr/bin/env python
""" Small pipeline for finding regions in a reference dequence (Rn45s) which
is mapped to by the poly-T region of reads in a formatted forward fastq file.
"""
import argparse
import subprocess
import os


def main(args):
    basename = os.path.splitext(os.path.basename(args.fastq))[0]

    # Map with standard trim settings
    trim5_full = args.bc_length + args.polyt_length + 2
    basename_1 = basename + '_mapped_t5_' + str(trim5_full)
    out_sam_1 = basename_1 + '.sam'
    bt2_call_1 = ['bowtie2', '-p', '4', '--sensitive']
    bt2_call_1 += ['-x', args.ref_index, '-U', args.fastq, '-S', out_sam_1]
    bt2_call_1 += ['--trim5', str(trim5_full)]
    if not os.path.exists(out_sam_1):
        print("")
        print(" ".join(bt2_call_1))
        if not args.dry_run:
            subprocess.check_call(bt2_call_1)

    # Get mapped reads to fastq
    mapped_fastq = basename_1 + '.fastq'
    filter_call = ['mapped_sam_fastq_filter.py', args.fastq, out_sam_1, mapped_fastq]
    if not os.path.exists(mapped_fastq):
        print(" ".join(filter_call))
        if not args.dry_run:
            subprocess.check_call(filter_call)

    # Map with multiple trimmings up to full trim
    basename_2 = basename_1 + '_mapped_t5_{}'
    trimmings = []
    i = 0
    while i * 3 < trim5_full:
        trim5 = i * 3
        trimmings.append(trim5)
        i += 1
        out_sam_2 = basename_2.format(str(trim5).zfill(2)) + '.sam'
        bt2_call_2 = ['bowtie2', '-p', '4', '--sensitive']
        bt2_call_2 += ['-x', args.ref_index, '-U', mapped_fastq, '-S', out_sam_2]
        bt2_call_2 += ['--trim5', str(trim5)]
        if not os.path.exists(out_sam_2):
            print(" ".join(bt2_call_2))
            if not args.dry_run:
                subprocess.check_call(bt2_call_2)

    # Convert sam files to sorted bam files
    convert_call_1 = ['samtools', 'view', '-bS', out_sam_1, '|']
    convert_call_1 += ['samtools', 'sort', '-', basename_1 + '_sorted']
    convert_call_1_str = r" ".join(convert_call_1)
    if not os.path.exists(basename_1 + '_sorted.bam'):
        print(convert_call_1_str)
        if not args.dry_run:
            subprocess.check_call(convert_call_1_str, shell=True)

    for trim5 in trimmings:
        out_sam_2 = basename_2.format(str(trim5).zfill(2)) + '.sam'
        convert_call_2 = ['samtools', 'view', '-bS', out_sam_2, '|']
        convert_call_2 += ['samtools', 'sort', '-', basename_2.format(str(trim5).zfill(2)) + '_sorted']
        convert_call_2_str = r" ".join(convert_call_2)
        if not os.path.exists(basename_2.format(str(trim5).zfill(2)) + '_sorted.bam'):
            print(convert_call_2_str)
            if not args.dry_run:
                subprocess.check_call(convert_call_2_str, shell=True)

    # Create bam index files
    index_call_1 = ['samtools', 'index', basename_1 + '_sorted.bam', basename_1 + '_sorted.bai']
    index_call_1_str = r" ".join(index_call_1)
    if not os.path.exists(basename_1 + '_sorted.bai'):
        print(index_call_1_str)
        if not args.dry_run:
            subprocess.check_call(index_call_1_str, shell=True)

    remapped_bams = []
    for trim5 in trimmings:
        remapped_bam = basename_2.format(str(trim5).zfill(2)) + '_sorted.bam'
        remapped_bams.append(remapped_bam)
        index_call_2 = ['samtools', 'index', remapped_bam,
                        basename_2.format(str(trim5).zfill(2)) + '_sorted.bai']
        index_call_2_str = r" ".join(index_call_2)
        if not os.path.exists(basename_2.format(str(trim5).zfill(2)) + '_sorted.bai'):
            print(index_call_2_str)
            if not args.dry_run:
                subprocess.check_call(index_call_2_str, shell=True)

    # Generate coverage statistics
    columns = ','.join(map(str, [2, 4] + [t + 7 for t in trimmings]))

    mpileup_call = ['samtools', 'mpileup', '-r', '"' + args.ref_name + '"']
    mpileup_call += ['-BQ0', '-d10000000']  # settings for only doing coverage stats
    mpileup_call += [basename_1 + '_sorted.bam']
    mpileup_call += remapped_bams
    mpileup_call += ['|', 'cut', '-f', columns, '-s']
    mpileup_call += ['>', basename + '_alignment_depths.csv']

    mpileup_call_str = r" ".join(mpileup_call)

    if not os.path.exists(basename + '_alignment_depths.csv'):
        print(mpileup_call_str)
        if not args.dry_run:
            subprocess.check_call(mpileup_call_str, shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fastq", help="Formatted fastq file with fw reads.")
    parser.add_argument("ref_index", help="Path to Bowtie2 index of reference sequence.")
    parser.add_argument("ref_name", help="Name of reference region, e.g. \
                                          gi|374429539|ref|NR_046233.1| for Rn45s \
                                          (as it appears in the BT2 index")
    parser.add_argument("--bc_length", help="Barcode length", type=int, default=27)
    parser.add_argument("--polyt_length", help="Poly-T region length", type=int, default=22)
    parser.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()
    main(args)
