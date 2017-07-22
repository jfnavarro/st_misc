#! /usr/bin/env python
# @Created by Jose Fernandez

"""Identify barcodes in a fastq file

Given a fastq file containing barcodes, this identifies
the barcode in each read and writes it into a unique file. Mismatches are
allowed and barcode position within the reads can be specified.

Usage:

    barcodeMapper.py [options] <barcode file> <in fastq file> <outputfile>
    
        --mismatch=n (number of allowed mismatches, (default 2))
        --kmer=n (number of bases of kmer, (default 7) When set to >1 it splits the barcodes into kmer size)
        --bc_offset=n (an offset into the read where the barcode starts (default 0))
        --global (use glocal pairwise alignment instead of local (default))
        --lenght=n (lenght of the barcode, (default 18))
        --noindel (disallow insertion/deletions on barcode matches)
        --quiet (do not print out summary information on tags)

<barcode file> is a text file of:

    <barcode> <x> <y>
    
for all barcodes present in the fastq it outputs :

<barcode> <x> <y> <Qul> <Read> <name>

"""

import sys
import os
import itertools
import collections
import csv
from optparse import OptionParser

from Bio import pairwise2
from Bio.SeqIO.QualityIO import FastqGeneralIterator


class Barcode:
    
    def __init__(self,seq,x,y):
        
        self.x = x
        self.y = y
        self.seq = seq


def main(barcode_file, out, in1, mismatch, bc_offset, kmer, allow_indels, bc_length, verbose, use_local_alignment, use_kmer_barcodes):
    
    if(verbose and use_local_alignment):
        print "Using local alignment"
    elif(verbose):
        print "Using local alignment"
    else:
        pass
    
    if(verbose and use_kmer_barcodes):
        print "Diving the barcodes into kmer of " + str(kmer)
    
    if(verbose):
        print "Allowing " + str(mismatch) + " number of mismatches"
        print "Barcode lenght " + str(bc_length)
        
    barcodes,barcodes_kmer = read_barcodes(barcode_file,kmer)  ##returns a dict of barcode => Barcode object (splitted in kmer and not)
    
    if(verbose):
        print "Number of barcodes present : " + str(len(barcodes))
        if(use_kmer_barcodes):
            print "Number of barcodes with kmer present : " + str(len(barcodes))
            
    out_handle = open(out,"w")
    
    stats = {}
        
    
    """ here I need to split fasta file in junks and run the loop for each junk in a thread """
    
    for (name1, seq1, qual1) in read_fastq(in1):
        
        end_gen = extract_barcode_from_read(seq1, bc_offset)
        
        bc_seq, x, y = best_match(end_gen, barcodes, barcodes_kmer, mismatch, bc_length, allow_indels, verbose, use_local_alignment, use_kmer_barcodes)
        
        if(bc_seq != "" and x != 0 and y != 0):
            out_handle.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (name1, seq1, qual1, bc_seq, str(x), str(y))) 
            if(stats.has_key(bc_seq)):
                stats[bc_seq] += 1
            else:
                stats[bc_seq] = 1

    #print some stats here
    if(verbose):
        print "Found : " + str(len(stats)) + " barcodes matching to reads"
    
    out_handler.close()
    
def best_match(end_gen, barcodes, barcodes_kmer, mismatch, bc_length, allow_indels=True, 
               verbose = False, use_local_alignment = True, use_kmer_barcodes = False):
    
    """Identify barcode best matching to the test sequence, with mismatch.
    Returns the barcode id, barcode sequence and match sequence.
    unmatched is returned for items which can't be matched to a barcode within
    the provided parameters.
    """
    
    # easiest, fastest case -- exact match

    test_seq = end_gen(bc_length)
    
    try:
        bc_id = barcodes[test_seq]
        if(verbose): print "OH, perfect match : " + str(bc_id.seq) + " in " + str(test_seq)
        return bc_id.seq, bc_id.x, bc_id.y
    except KeyError:
        pass

    # check for best approximate match within mismatch values 
    match_info = []
    
    if _barcode_very_ambiguous(barcodes):  
        gapopen_penalty = -18.0
    else:
        gapopen_penalty = -9.0
    
    if(use_kmer_barcodes): barcodes = barcodes_kmer
        
    if mismatch > 0 or _barcode_has_ambiguous(barcodes): 
        
        for bc_seq, bc_object in barcodes.iteritems():  
            
            # Do local or global alignment, when global alignment.  Identical characters are given 5 points,
            # -4 point is deducted for each non-identical character. <gapopen_penalty> points are deducted when opening a
            # gap, and 0.5 points are deducted when extending it
            
            ## SHOULD USE UNGAPPED ALINGMENT
            
            if(use_local_alignment):
                aligns = pairwise2.align.localxx(bc_seq, test_seq, one_alignment_only=True)
            else:
                aligns = pairwise2.align.globalms(bc_seq, test_seq, 5.0, -4.0, gapopen_penalty, -0.5, one_alignment_only=True)
            
            (abc_seq, atest_seq) = aligns[0][:2] if len(aligns) == 1 else ("", "")
            
            gaps = abc_seq.count("-")
            
            matches = sum(1 for i, base in enumerate(abc_seq) if (base == atest_seq[i] or base == "N"))
            
            #cur_mismatch = (len(test_seq) - matches + gaps)  ## include gaps in miss matches?
            cur_mismatch = (len(test_seq) - matches) 
            
            if cur_mismatch <= mismatch and (allow_indels or gaps == 0): 
                match_info.append((cur_mismatch, bc_object, abc_seq, test_seq))
                break ## stops at first good match
            
    if len(match_info) > 0:
        
        match_info.sort()
        
        bc_object, bc_seq, test_seq = match_info[0][1:]
        
        bc_seq_matched = bc_seq.replace("-", "")
        
        if(verbose): print "possible of barcode : " + str(bc_object.seq) + " with matched sequence " + str(bc_seq_matched) + " and raw read sequence " + str(test_seq)
        
        return bc_object.seq, bc_object.x, bc_object.y
    
    else:
        return "", 0, 0

def _barcode_very_ambiguous(barcodes):
    
    """ consider replace N for T """
    
    max_size = max(len(x) for x in barcodes.keys())
    max_ns = max(x.count("N") for x in barcodes.keys())
    return float(max_ns) / float(max_size) > 0.5

def _barcode_has_ambiguous(barcodes):
    
    """ consider replace N for T """
    
    for seq in barcodes.keys():
        if "N" in seq:
            return True
    return False

def extract_barcode_from_read(seq1, bc_offset = 0):
    
    """Function which pulls a barcode of a provided size from paired seqs.

    This respects the provided details about location of the barcode, returning
    items of the specified size to check against the read.
    
    """
    def _get_end(size):
        assert size > 0
        return seq1[bc_offset:size+bc_offset]
    return _get_end

def read_barcodes(fname,kmer = 1):
    
    """ exctracts barcodes and cordinate from id file, 
    creates two maps one with full barcodes and another with sliced barcodes into kmer """
    
    barcodes = {}
    barcodes_kmer = {}
    with open(fname) as in_handle:
        for line in (l for l in in_handle if not l.startswith("#")):
            seq, x, y = line.rstrip("\t").split()
            barcodes[seq] = Barcode(seq,x,y)
            for sliced in [seq[i:i+kmer] for i in range(0, len(seq),kmer)]:
                if(len(sliced) >= kmer):
                    barcodes_kmer[sliced] = Barcode(seq,x,y)
            
    return barcodes,barcodes_kmer

def read_fastq(fname):
    """Provide read info from fastq file, potentially not existing."""
    if fname:
        with open(fname) as in_handle:
            for info in FastqGeneralIterator(in_handle):
                yield info
    else:
        for info in itertools.repeat(("", None, None)):
            yield info
            
if __name__ == "__main__":
    
    parser = OptionParser()
    parser.add_option("-i", "--noindel", dest="indels",action="store_false", default=True)
    parser.add_option("-q", "--quiet", dest="verbose",action="store_false", default=True)
    parser.add_option("-g", "--global", dest="use_local_alignment",action="store_false", default=True)
    parser.add_option("-m", "--mismatch", dest="mismatch", default=2)
    parser.add_option("-k", "--kmer", dest="kmer", default=1)
    parser.add_option("-l", "--length", dest="length", default=18)
    parser.add_option("-b", "--bc_offset", dest="bc_offset", default=0)

    options, args = parser.parse_args()
    if len(args) == 3:
        barcode_file, in1, out = args
    else:
        print __doc__
        sys.exit()
    
    use_kmer_barcodes = True if int(options.kmer) > 1 else False
    
    main(barcode_file, out, in1, int(options.mismatch), int(options.bc_offset),
         int(options.kmer), options.indels, int(options.length),options.verbose,options.use_local_alignment,use_kmer_barcodes)

