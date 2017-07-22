#! /usr/bin/env python
# @Created by Jose Fernandez
""" Complete definition here
"""

from datetime import datetime
import getopt
import sys
import os
from glob import glob
import threading
import subprocess
from itertools import izip
import resource
import gc

from collections import namedtuple
_ntuple_diskusage = namedtuple('usage', 'total used free')
                      
try:
    import pysam
except ImportError, e:
    sys.stderr.write("PySam was not found\n")
    sys.exit(1)

try:
    import HTSeq
except Exception:
    sys.stderr.write("HTSeq was not found\n")
    sys.exit(1)
    

''' A simple user friendly GUI would be great '''
    
''' Study portability to the cloud, perhaps mapReduce to split files'''

''' improve stats with more information ''' 

''' break functionality into pieces, create classes to wrap common utilities (fasta parsers, file management...) '''

def Using(point):
    """ returns memory usage at a certain point 
    """
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           '''%(point,usage[0],usage[1],
                (usage[2]*resource.getpagesize())/1000000.0) 

class TimeStamper(object):
    ''' thread safe time stamper 
    '''
    def __init__(self):
        self.lock = threading.Lock()
        self.prev = None
        self.count = 0

    def getTimestamp(self):
        with self.lock:
            ts = datetime.now()
            if ts == self.prev:
                ts += '.%04d' % self.count
                self.count += 1
            else:
                self.prev = ts
                self.count = 1
        return ts

class Stats(object):
    ''' thread safe stats writer 
    '''
    
    def __init__(self,name):
        self.lock = threading.Lock()
        self.name = name
        self.handler = open(name,"w")
    
    def write(self,text):
        with self.lock:
            self.handler.write(text)
        
    def close(self):
        with self.lock:
            self.handler.close()

def disk_usage(path):
    """Return disk usage statistics about the given path 
    """   
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)

def safeRemove(filename):
    ''' safely remove a file 
    '''
    try:
        if(os.path.isfile(filename)):
            os.remove(filename)
    except UnboundLocalError:
        pass
        
def safeOpenFile(filename,atrib):
    ''' safely opens a file 
    '''
    
    if(atrib.find("w") != -1):
        safeRemove(filename)
        usage = disk_usage('/')
        if(usage.free <= 1073741824): ## at least 1GB
            sys.stderr.write("Error : no free space available\n")
            sys.exit()
    elif(atrib.find("r") != -1):
        if(not os.path.isfile(filename)):  # is present?
            sys.stderr.write("Error : " + filename + " not found\n")
            sys.exit()
    else:
        sys.stderr.write("Error : wrong attribute " + atrib + " opening file\n")
        sys.exit()

    handler = open(filename, atrib)
    return handler


def fileOk(_file):
    ''' checks file exists and is not zero size
    '''
    if(not os.path.isfile(_file) or os.path.getsize(_file) == 0):
        return False
    else:
        return True

def usage():
    print "Usage:"
    print "analysisPipeline.py reads_fw.fastq reads_rv.fastq [parameters]"
    print "Where [parameters] are :"
    print "[-i, --ids <file>] = the name of the file containing the " \
          "barcodes and the coordinates => REQUIRED"
    print "[-M, --ref-map <path_to_bowtie2_indexes>] = reference genome name for the " \
          "genome that you want to use to align the reads => REQUIRED"
    print "[-a, --ref-annotation <file>] =  select the reference(htseq requires a GTF file) " \
          "annotation file that you want to use to annotate => REQUIRED"
    print "[-N, --lane-name <string>] = the name and number of the lane"
    print "[-E, --expName <string>] = the name of the experiment"
    print "[-v, --verbose] = activate verbose mode to show useful information " \
          "on the screen"
    print "[-m, --allowed-missed <integer>] = number of allowed mismatches " \
          "when mapping against the barcodes, default 3"
    print "[-k, --allowed-kimer <integer>] = kMer length when mapping against " \
          "the barcodes, default is 6"
    print "[-f, --min-length-qual-trimming <integer>] = minimum lenght of the " \
          "sequence for mapping after trimming, shorter reads will be discarded " \
          ", default 28"
    print "[-F, --mapping-fw-trimming <integer>] => the number of bases to " \
          "trim in the forward reads for the Mapping [24 + ID_LENGTH], default is 42"
    print "[-R, --mapping-rw-trimming <integer>] => the number of bases to " \
          "trim in the reverse reads for the Mapping , default is 5"
    print "[-l, --length-id <integer>] => length of ID, a.k.a. the length of " \
          "the barcodes, default 18"
    print "[--contaminant-bowtie2-index <path_to_bowtie2_indexes>] => " \
          "When provided, reads will be filtered against the specified " \
          "bowtie2 index, non-mapping reads will be saved and demultiplexed."
    print "[-h, --help] => show extended help"

def usagePro():
    print "Developer options :"
    print "[-q, --qual-64] = use phred-64 quality instead of phred-33(default)"
    print "[--htseq-mode <mode>] = Mode of Annotation when using HTSeq. " \
	  "Modes = {union,intersection-nonempty(default),intersection-strict}"
    print "[--htseq-no-ambiguous] = When using htseq discard reads annotating ambiguous genes."   
    print "[-s, --start-id <integer>] => start position of BARCODE ID [0], default 0"
    print "[-e, --error-id <integer>] => Id positional error [0], default 0"
    print "[-C, --no-clean-up] => do not remove temporary files at the end (useful for debugging)"
    print "[-T, --bowtie-threads <integer>] => number of threads to use in bowtie2 (default 8)"
    print "[-Q, --min-quality-trimming <integer>] => minimum quality for trimming (default 20)"
    print "[-W, --discard-fw] => discard fw reads that maps uniquely"
    print "[-Y, --discard-rw] => discard rw reads that maps uniquely"
    print "[--bowtie2-discordant] => include non-discordant alignments when mapping"

def stripExtension(string):
    f = string.rsplit('.', 1)
    if(f[0].find("/") != -1):
        return f[0].rsplit('/', 1)[1]

    else:
        return f[0]

def getExtension(string):
    f = string.rsplit('.', 1)
    return f[1]

def bowtie2Map(fw, rv, ref_map, statFile, trim = 42, cores = 8, qual64 = False, discordant = True):  
    ''' maps pair end reads against given genome using bowtie2 
    '''
    
    if(verbose): print "Start Bowtie2 Mapping at : " + str(globaltime.getTimestamp())
    
    if fw.endswith(".fastq"):
        outputFile = stripExtension(fw) + ".sam"
    else:
        sys.stderr.write("Error: Input format not recognized\n")
        sys.exit()
    
    qual_flags = ["--phred64"] if qual64 else ["--phred33"] 
    core_flags = ["-p", str(cores)] if cores > 1 else []
    trim_flags = ["--trim5",trim] 
    io_flags   = ["-q","-X",2000,"--sensitive"] ##500 (default) is too selective
    io_flags  += ["--no-discordant"] if discordant else []
    
    args = [os.environ['HOME'] + '/bin/bowtie2']
    args += trim_flags
    args += qual_flags
    args += core_flags
    args += io_flags

    args += ["-x", ref_map, "-1", fw, "-2", rv, "-S", outputFile] 

    proc = subprocess.Popen([str(i) for i in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, errmsg) = proc.communicate()

    if(not fileOk(outputFile)):
        sys.stderr.write("Error: doing bowtie...are the indexes present and compatible?\n")
        sys.stderr.write(stdout + "\n")
        sys.stderr.write(errmsg + "\n")
        sys.exit()
    else:
        procOut = [x for x in errmsg.split("\n") if x.find("Warning") == -1 and x.find("Error") == -1]
        statFile.write('\nMapping stats on paired end mode with 5-end trimming of ' + str(trim) + '\n')
        for line in procOut:
            statFile.write(str(line) + '\n')

    if(verbose):
        print "Finish Bowtie2 Mapping at : " + str(globaltime.getTimestamp())

    return outputFile


def bowtie2_contamination_map(fastq, contaminant_index, statFile, trim=42,
                              cores=8, qual64=False):
    """ Maps reads against contaminant genome index with Bowtie2 and returns
    the fastq of unaligned reads.
    """
    if verbose:
        print "Start Bowtie2 contaminant mapping at : " + str(globaltime.getTimestamp())

    if fastq.endswith(".fastq"):
        contaminated_file = stripExtension(fastq) + "_contaminated.sam"
        clean_fastq = stripExtension(fastq) + "_clean.fastq"

    else:
        sys.stderr.write("Error: Input format not recognized\n")
        sys.exit()

    qual_flags = ["--phred64"] if qual64 else ["--phred33"]
    core_flags = ["-p", str(cores)] if cores > 1 else []
    trim_flags = ["--trim5", trim]
    io_flags   = ["-q","--sensitive"]

    args = [os.environ['HOME'] + '/bin/bowtie2']

    args += trim_flags
    args += qual_flags
    args += core_flags
    args += io_flags

    args += ["-x", contaminant_index, "-U", fastq, "-S", contaminated_file, "--un", clean_fastq]

    proc = subprocess.Popen([str(i) for i in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, errmsg) = proc.communicate()

    if not fileOk(contaminated_file) or not fileOk(clean_fastq):
        sys.stderr.write("Error: doing bowtie...are the indexes present and compatible?\n")
        sys.stderr.write(stdout + "\n")
        sys.stderr.write(errmsg + "\n")
        sys.exit()

    else:
        procOut = [x for x in errmsg.split("\n") if x.find("Warning") == -1 and x.find("Error") == -1]
        statFile.write('\nContaminant mapping stats against ' +
                       contaminant_index + ' with 5-end trimming of ' +
                       str(trim) + '\n')

        for line in procOut:
            statFile.write(str(line) + '\n')

    if verbose:
        print "Finish Bowtie2 contaminant mapping at : " + str(globaltime.getTimestamp())

    return clean_fastq, contaminated_file


def filterUnmapped(sam, discard_fw=False, discard_rw=False):
    ''' filter unmapped and discordant reads
    '''
    if(verbose):
        print "Start converting Sam to Bam at : " + str(globaltime.getTimestamp())

    if sam.endswith(".sam"):
        outputFileSam = stripExtension(sam) + '_filtered.sam'
    else:
        sys.stderr.write("Error: Input format not recognized for file " + file + "\n")
        sys.exit()

    # Remove found duplicates in the Forward Reads File
    input = pysam.Samfile(sam, "r")
    output = pysam.Samfile(outputFileSam, 'wh', header=input.header)

    for read in input:
        # filtering out pair end reads
        if(not read.is_paired):
            sys.stderr.write("Error: input Sam file contains not paired reads\n")
            sys.exit()

        if(read.is_proper_pair and not read.mate_is_unmapped):
            # if read is a concordant pair and is mapped write
            output.write(read)
        elif(not read.is_proper_pair and not read.is_unmapped):
            # if read is a discordant mapped pair or uniquely mapped (mixed mode bowtie2)
            if(read.is_read1 and not discard_fw):
                # if read is forward and I dont want to discard it
                output.write(read)
            elif(read.is_read2 and not discard_rw):
                 # if read is reverse and I dont want to discard it
                output.write(read)
            else:
                # I want to discard both forward and reverse and unmapped
                pass
        else:
            # not mapped stuff discard
            pass  
            
    input.close()
    output.close()

    if(not fileOk(outputFileSam)):
        sys.stderr.write("Error: filtering Sam file " + str(retcode) + " file " + sam + "\n")
        sys.exit()
    
    return outputFileSam

def annotateReadsWithHTSeq(samFile, gtfFile, mode):
    ''' Annotate the reads using htseq-count utility 
    '''
    
    if(verbose):
        print "Annotating reads with HTSeq at : " + str(globaltime.getTimestamp())
    
    if samFile.endswith(".sam"):
        outputFile = stripExtension(samFile) + '_gene.sam'
    else:
        sys.stderr.write("Error: Input format not recognized\n")
        sys.exit()
    
    discard_output = open(os.devnull,"w")
    
    args = ['htseq-count',"-m",mode,"-s","no","-i","gene_id" ,"-o",outputFile,samFile,gtfFile]
    subprocess.check_call(args,stdout=discard_output, stderr=subprocess.PIPE)
    
    if(not os.path.isfile(outputFile) or os.path.getsize(outputFile) == 0 ):
        sys.stderr.write("Error: annotating reads with HTSeq \n")
        sys.exit()
        
    if(verbose):
        print "Annotating reads with HTSeq at :" + str(globaltime.getTimestamp())
    
    return outputFile

def getAllMappedReadsSam(annot_reads, htseq_no_ambiguous = False):
    ''' creates a map with the read names that are annotated and mapped and 
        their mapping scores,chromosome and gene
        We assume the gtf file has its gene ids replaced by gene names
    '''
    filter = ["no_feature","ambiguous",
              "too_low_aQual","not_aligned",
              "alignment_not_unique"]
    
    mapped = dict()
    sam = HTSeq.SAM_Reader(annot_reads)
    
    for alig in sam:
        
        gene_name = str(alig.optional_field("XF"))
        if gene_name in filter or not alig.aligned or \
        (htseq_no_ambiguous and gene_name.find("ambiguous") != -1):
            continue
        
        strand = str(alig.pe_which)
        name = str(alig.read.name) 
        #seq = str(alig.read.seq)
        #qual = str(alig.read.qualstr)
        mapping_quality = int(alig.aQual)
        
        if alig.mate_start:
            chromosome = alig.mate_start.chrom 
        else:
            chromosome = "Unknown"
            
        if strand == "first":
            name += "/1"
        elif strand == "second":
            name += "/2"
        else:
            print "Warning : un-strander read " + str(name)
            continue ## not possible
        
        mapped[name] = (mapping_quality,gene_name,chromosome)  # there should not be collisions
        
    return mapped

def getAnnotatedReadsFastq(annot_reads, fw, rv, statFile, use_htseq = None , htseq_no_ambiguous = False):  
    ''' I get the forward and reverse reads,qualities and sequences that are annotated
        and mapped (present in annot_reads)
    '''
    if(verbose):
        print "Start Mapping to Transcripts at : " + str(globaltime.getTimestamp())
    
    if (annot_reads.endswith(".sam") ) \
        and fw.endswith(".fastq") and rv.endswith(".fastq"):
        outputFile = stripExtension(fw) + '_withTranscript.fastq'
    else:
        sys.stderr.write("Error: Input format not recognized\n")
        sys.exit()
        
    #Find all mapped!
    if annot_reads.endswith(".sam") and use_htseq:
        mapped = getAllMappedReadsSam(annot_reads, htseq_no_ambiguous)
    else:
        sys.stderr.write("Error: Incorrect Input Format\n")
        sys.exit()
    
    if(len(mapped) == 0):
        sys.stderr.write("Error, annotated read file does not contain valid records\n")
        sys.exit()
    else:
        readMappingToTranscript = len(mapped)
    
    outF = safeOpenFile(outputFile,'w')
    outF_writer = writefq(outF)
    fw_file = safeOpenFile(fw, "rU")
    rv_file = safeOpenFile(rv, "rU")
    
    #from the raw fw and rv reads write the records that have been mapped and annotated 
    for line1,line2 in izip( readfq(fw_file) , readfq(rv_file) ):

        #we add this to match the reads to the extra symbol added by bowtie in pair end mode
        name1 = (line1[0] + "/1") if line1[0].find("/1") == -1 else line1[0]
        name2 = (line2[0] + "/2") if line2[0].find("/2") == -1 else line2[0]
        mappedFW = mapped.has_key(name1)
        mappedRV = mapped.has_key(name2)
        
        if(mappedFW and mappedRV): #fw and rv mapped and annotated
            
            if(mapped[name1][0] > mapped[name2][0]): #pick highest scored
                new_line1 = ( (name1 + " Chr:" +  mapped[name1][2] + " Gene:" + mapped[name1][1]), line1[1], line1[2] )
                outF_writer.send(new_line1)
            else:
                new_line2 = ( (name2 + " Chr:" +  mapped[name2][2] + " Gene:" + mapped[name2][1]), line2[1], line2[2] ) 
                outF_writer.send(new_line2)
                
        elif(mappedFW):  # only fw mapped and annotated    
            new_line1 = ( (name1 + " Chr:" +  mapped[name1][2] + " Gene:" + mapped[name1][1]), line1[1], line1[2] )        
            outF_writer.send(new_line1)    
            
        elif(mappedRV):
            new_line2 = ( (name2 + " Chr:" +  mapped[name2][2] + " Gene:" + mapped[name2][1]), line2[1], line2[2] )
            outF_writer.send(new_line2)  # only rv mapped and annotated
            
        else:
            pass
            #neither fw or rw are annotated and mapped

    outF_writer.close()
    outF.close()
    fw_file.close()
    rv_file.close()
    
    if(not fileOk(outputFile)):
        sys.stderr.write("Error: Mapping to transcripts\n")
        sys.exit()
    else:
        statFile.write('\nTotal reads mapping to a transcript : ' + str(readMappingToTranscript) + '\n')
        
    if(verbose):
        print "Finish Mapping to Transcripts at : " + str(globaltime.getTimestamp())
        
    return outputFile


def getTrToIdMap(readsContainingTr, idFile, m, k, s, l, e, statFile):
    ''' barcode mapping with old findindexes 
    '''
    
    if(verbose):
        print "Start Mapping against the barcodes at : " + str(globaltime.getTimestamp())
    
    outputFile = stripExtension(readsContainingTr) + '_nameMap.txt'

    args = [os.environ['HOME'] + '/bin/findIndexes',
            "-m", str(m), "-k", str(k), "-s", str(s),
            "-l", str(l), "-o", str(outputFile), idFile,
            readsContainingTr]

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, errmsg) = proc.communicate()
 
    if not os.path.isfile(outputFile) or os.path.getsize(outputFile) == 0:
        sys.stderr.write("Error: Mapping against the barcodes\n")
        sys.exit()
 
    else:
        procOut = stdout.split("\n")
        statFile.write('\nBarcode Mapping stats : \n')
        for line in procOut: 
            statFile.write(str(line) + '\n')

    if(verbose):
        print "Finish Mapping against the barcodes at : " + str(globaltime.getTimestamp())
    
    return outputFile

def createDatabase(mapFile, collName, dbName, statFile):
    ''' parse annotated and mapped reads with the reads that contain barcodes to
        create json files with the barcodes and cordinates and json file with the raw reads
        and some useful stats and plots
    '''
    
    if(verbose):print "Start Creating databases " + str(globaltime.getTimestamp())
    
    args = ['createDatabase.py',str(mapFile),str(collName),str(dbName)]

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, errmsg) = proc.communicate()
        
    procOut = stdout.split("\n")
    statFile.write('\nCreate Database stats : \n')
    for line in procOut: 
        statFile.write(str(line) + '\n')
            
    if(verbose):print "Finish Creating databases " + str(globaltime.getTimestamp())

    return

def coroutine(func):
    """ Coroutine decorator, starts coroutines upon initialization.
    """
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr

    return start

def trim_quality(record, trim_distance, min_qual = 20, 
                 min_length = 28,qual64=False):    
    ''' perfoms a bwa-like quality trimming on the sequence and 
    quality in tuple record(name,seq,qual)
    '''
    qscore = record[2]
    sequence = record[1]
    name = record[0]
    nbases = 0
    phred = 64 if qual64 else 33
    
    for qual in qscore[::-1]:
        if ( ord(qual) - phred ) < min_qual:
            nbases +=1
    
    if ( (len(sequence) - (trim_distance + nbases)) >= min_length):
        new_seq = record[1][:(len(sequence) - nbases)]
        new_qual = record[2][:(len(sequence) - nbases)]
        return name,new_seq,new_qual
    else:
        return None

def getFake(record):
    ''' generates a fake fastq record(name,seq,qual) from the record given as input
    '''
    new_seq = "".join("N" for k in record[1])
    new_qual = "".join("B" for k in record[2])
    return (record[0],new_seq,new_qual)

def readfq(fp): # this is a generator function
    """ Heng Li's fasta/fastq reader function.
    """
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq):  # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs)  # yield a fastq record
                    break
            if last:  # reach EOF before reading enough quality
                yield name, seq, None  # yield a fasta record instead
                break


@coroutine
def writefq(fp):  # This is a coroutine
    """ Fastq writing generator sink.
    Send a (header, sequence, quality) triple to the instance to write it to
    the specified file pointer.
    """
    fq_format = '@{header}\n{sequence}\n+\n{quality}\n'
    try:
        while True:
            record = yield
            read = fq_format.format(header=record[0], sequence=record[1], quality=record[2])
            fp.write(read)

    except GeneratorExit:
        return


def reformatRawReads(fw, rw, statFile, trim_fw=42, trim_rw=5,
                     min_qual=20, min_length=28, qual64=False):
    """ Converts reads in rw file appending the first (distance - trim)
    bases of fw and also add FW or RW string to reads names
    It also performs a bwa qualitry trim of the fw and rw reads, when
    the trimmed read is below min lenght it will discarded.
    """
    if(verbose):
        print "Start Reformating and Filtering raw reads at : " + str(globaltime.getTimestamp())

    if fw.endswith(".fastq") and rw.endswith(".fastq"):
        out_rw = stripExtension(rw) + '_formated.fastq'
        out_fw = stripExtension(fw) + '_formated.fastq'

    else:
        sys.stderr.write("Error: Input format not recognized\n")
        sys.exit()

    out_fw_handle = safeOpenFile(out_fw, 'w')
    out_fw_writer = writefq(out_fw_handle)
    out_rw_handle = safeOpenFile(out_rw, 'w')
    out_rw_writer = writefq(out_rw_handle)

    fw_file = safeOpenFile(fw, "rU")
    rw_file = safeOpenFile(rw, "rU")

    total_reads = 0
    dropped_fw = 0
    dropped_rw = 0
    nbases = int(trim_fw) - int(trim_rw)

    for line1, line2 in izip(readfq(fw_file), readfq(rw_file)):
        total_reads += 1

        # Trim rw
        line2_trimmed = trim_quality(line2, trim_rw, min_qual, min_length, qual64)
        # Trim fw
        line1_trimmed = trim_quality(line1, trim_fw, min_qual, min_length, qual64)

        if line1_trimmed is not None:
            out_fw_writer.send(line1_trimmed)
        else:
            # I want to write fake sequence so bowtie wont fail
            out_fw_writer.send(getFake(line1))
            dropped_fw += 1

        if line2_trimmed is not None:
            # Add the barcode and polyTs from fw only if rw has not been completely trimmed
            new_seq = line1[1][:nbases] + line2_trimmed[1]
            new_qual = line1[2][:nbases] + line2_trimmed[2]
            record = (line2_trimmed[0], new_seq, new_qual)
            out_rw_writer.send(record)

        else:
            # I want to write fake sequence so bowtie wont fail
            out_rw_writer.send(getFake(line2))
            dropped_rw += 1  
    
    out_fw_writer.close()
    out_rw_writer.close()
    out_fw_handle.close()
    out_rw_handle.close()
    fw_file.close()
    rw_file.close()
    
    if not fileOk(out_fw) or not fileOk(out_rw):
        sys.stderr.write("Error: Reformating and Filtering raw reads \n")
        sys.exit()
    else:
        statFile.write("\nTrimming stats fw 1 : " + str(dropped_fw) + " reads have been dropped on the forward reads!\n")
        perc1 = '{percent:.2%}'.format(percent= float(dropped_fw) / float(total_reads) )
        statFile.write("Trimming stats fw 2 : you just lost about " + perc1 + " of your data on the forward reads!\n")
        statFile.write("\nTrimming stats rw 1 : " + str(dropped_rw) + " reads have been dropped on the reverse reads!\n") 
        perc2 = '{percent:.2%}'.format(percent= float(dropped_rw) / float(total_reads) )
        statFile.write("Trimming stats rw 2 : you just lost about " + perc2 + " of your data on the reverse reads!\n")
        
    if(verbose):
        print "Finish Reformating and Filtering raw reads at : " + str(globaltime.getTimestamp())
    
    return out_fw, out_rw


def main(argv):
    
    global verbose
    global globaltime
    globaltime = TimeStamper()
    allowed_missed = 3
    allowed_kimera = 6
    min_length_trimming = 28
    trimming_fw_bowtie = 42
    trimming_rw_bowtie = 5 
    min_quality_trimming = 20 
    clean = True
    s = 0
    l = 18
    e = 0
    threads = 8
    verbose = False
    ids = ""
    ref_map = ""
    ref_annotation = ""
    lane_name = ""
    expName = ""
    htseq_mode = "intersection-nonempty"
    htseq_no_ambiguous = False
    qual64 = False
    discard_fw = False
    discard_rv = False
    discordant = True
    contaminant_bt2_index = None
    
    if(len(argv) == 1 and argv[0] in ("-h", "--help")):
        usage()
        usagePro()
        sys.exit()
    elif len(argv) < 2:
        sys.stderr.write("Error: Number of arguments incorrect\n")
        usage()
        sys.exit()
    else:
        try:
            opts, args = getopt.getopt(sys.argv[3:], "hvm:k:f:e:s:l:N:i:M:a:E:CT:F:R:Q:qWY",
                                       ["help", "verbose", "allowed-missed=", "allowed-kimera=", "min-length-qual-trimming=",
                                        "error-id=", "start-id=", "lenght-id=",
                                        "lane-name=", "ids=", "ref-map=", "ref-annotation=", "expName=",
                                        "no-clean-up", "bowtie-threads=", "mapping-fw-trimming=", "mapping-rw-trimming=",
                                        "min-quality-trimming=", "qual-64","discard-fw", "discard-rw", 
                                        "htseq-mode=","contaminant-bowtie2-index=","htseq-no-ambiguous","bowtie2-discordant"])

        except getopt.GetoptError, err:
            # print help information and exit:
            print str(err)  # will print something like "option -a not recognized"
            usage()
            sys.exit(2)

        for o, a in opts:
            if o in ("-v", "--verbose"):
                verbose = True
            elif o in ("-h", "--help"):
                usage()
                usagePro()
                sys.exit()
            elif o in ("-m", "--allowed-missed"):
                allowed_missed = int(a)
            elif o in ("-k", "--allowed-kimera"):
                allowed_kimera = int(a)
            elif o in ("-f", "--min-length-qual-trimming"):
                min_length_trimming = int(a)
            elif o in ("-e", "--error-id"):
                e = int(a)
            elif o in ("-s", "--start-id"):
                s = int(a)
            elif o in ("-N", "--lane-name"):
                lane_name = str(a)
            elif o in ("-E", "--expName"):
                expName = str(a)
            elif o in ("-i", "--ids"):
                ids = str(a)
            elif o in ("-M", "--ref-map"):
                ref_map = str(a)
            elif o in ("-a", "--ref-annotation"):
                ref_annotation = str(a)
            elif o in ("-l", "--length-id"):
                l = int(a)
            elif o in ("-C", "--no-clean-up"):
                clean = False
            elif o in ("-T", "--bowtie-threads"):
                threads = int(a)
            elif o in ("-F", "--mapping-fw-trimming"):
                trimming_fw_bowtie = int(a)
            elif o in ("-R", "--mapping-rw-trimming"):
                trimming_rw_bowtie = int(a)
            elif o in ("-Q", "--min-quality-trimming"):
                min_quality_trimming = int(a)
            elif o in ("--htseq-mode"):
                htseq_mode = str(a)
            elif o in ("--htseq-no-ambiguous"):
                htseq_no_ambiguous = True
            elif o in ("-q", "--qual-64"):
                qual64 = True
            elif o in ("-W", "--discard-fw"):
                discard_fw = True
            elif o in ("-Y", "--discard-rw"):
                discard_rv = True
            elif o in ("--contaminant-bowtie2-index"):
                contaminant_bt2_index = str(a)
            elif o in ("--bowtie2-discordant"):
                discordant = False
            else:
                assert False, "unhandled option"   

        conds = {"FW": fileOk(argv[0]), "RV": fileOk(argv[1]), "ids": fileOk(ids), "ref": fileOk(ref_annotation), "map": ref_map != ""}
        conds["htseq_gtf"] = ref_annotation.endswith("gtf")
        conds["htseq_mode"] = htseq_mode in ["union","intersection-nonempty","intersection-strict"]

        if all(conds.values()):
            Fastq_fw = argv[0]
            Fastq_rv = argv[1]
        else:
            sys.stderr.write("Error: required file/s and or parameters not found or incorrect parameters\n")
            print(conds)
            sys.exit()

    #test the presence of the scripts :
    required_scripts = set([
        '/bin/findIndexes',
        '/bin/samtools',
        '/bin/bowtie2'])

    strip_home = lambda path: path.partition(os.environ["HOME"])[-1]
    available_scripts = set([strip_home(path) for path in glob(os.environ["HOME"] + "/bin/*")])
    unavailable_scripts = required_scripts - available_scripts
    
    if len(unavailable_scripts) == 0:
        print("All tools present..starting the analysis")
    else:
        sys.stderr.write("Error, these programs not found:\n\tHOME" +
                         ("\n\tHOME".join(unavailable_scripts)) + "\n")
        sys.exit()

    #show configuration information
    if(lane_name == ""):
        lane_name = "lane01"
        
    if(expName == ""):
        expName = stripExtension(Fastq_fw)

    #opens stats file
    statFileName = expName + "_" + lane_name + "_stats.txt"
    statFile = Stats(statFileName)

    #starting time
    start_exe_time = globaltime.getTimestamp()

    #show parameters information and write them to stats
    parameters = "Parameters : m(" + str(allowed_missed) + ")" + \
                 "k(" + str(allowed_kimera) + ")" + "f(" + str(min_length_trimming) + ")" + \
                 "e(" + str(e) + ")" + "s(" + str(s) + ")" + "l(" + str(l) + ")" + \
                 "F(" + str(trimming_fw_bowtie) + ")" + "R(" + str(trimming_rw_bowtie) + ")"

    print "Experiment Name : " + str(expName) + " Lane " + str(lane_name)
    print "Forward reads file : " + str(Fastq_fw)
    print "Reverse reads file : " + str(Fastq_rv)
    print "Ids file : " + str(ids)
    print "Reference mapping file : " + str(ref_map)
    print "Reference annotation file : " + str(ref_annotation)
    if(contaminant_bt2_index):
        print "Using bowtie2 contamination filter with " + str(contaminant_bt2_index)
    print "Nodes : " + str(threads)
    print parameters
    print "Mapper : bowtie2"
    print "Annotation Tool : HTSeq"

    statFile.write("Experiment : " + str(expName) + " Lane " + str(lane_name) + "\n")
    statFile.write("Forward reads file : " + str(Fastq_fw) + "\n")
    statFile.write("Reverse reads file : " + str(Fastq_rv) + "\n")
    statFile.write("Ids file : " + str(ids) + "\n")
    statFile.write("Reference mapping file : " + str(ref_map) + "\n")
    statFile.write("Reference annotation file : " + str(ref_annotation) + "\n")
    if(contaminant_bt2_index):
        statFile.write("Using bowtie2 contamination filter with " + str(contaminant_bt2_index) + "\n")
    statFile.write("Nodes : " + str(threads) + "\n")
    statFile.write(parameters + "\n")
    statFile.write("Mapper : bowtie2\n")
    statFile.write("Annotation Tool :  HTSeq\n")

    ################################ STARTING THE PIPELINE #############################################################

    # add BC and PolyT from FW reads to the RW reads and apply quality filter

    Fastq_fw_trimmed, Fastq_rv_trimmed = reformatRawReads(Fastq_fw, Fastq_rv, statFile, trimming_fw_bowtie,
                                                          trimming_rw_bowtie, min_quality_trimming,
                                                          min_length_trimming, qual64)

    # First, do mapping against genome of both strands
    sam_mapped = bowtie2Map(Fastq_fw_trimmed, Fastq_rv_trimmed, ref_map, 
                            statFile, trimming_fw_bowtie, threads, qual64, discordant)

    ## filter unmapped and discordant reads
    sam_filtered = filterUnmapped(sam_mapped, discard_fw, discard_rv)

    if(clean):
        safeRemove(sam_mapped)  

    ##annotate using htseq count
    annotatedFile = annotateReadsWithHTSeq(sam_filtered, ref_annotation, htseq_mode)
        
    if(clean):
        safeRemove(sam_filtered)

    # get raw reads and quality from the forward and reverse reads
    withTr = getAnnotatedReadsFastq(annotatedFile, Fastq_fw_trimmed, 
                                    Fastq_rv_trimmed, statFile, htseq_no_ambiguous)

    if(clean):
        safeRemove(annotatedFile)

    # Filter out contaminated reads with Bowtie2
    if contaminant_bt2_index:
        withTr, contaminated_sam = bowtie2_contamination_map(withTr, contaminant_bt2_index,
                                                             statFile, trim=trimming_fw_bowtie,
                                                             cores=threads, qual64=qual64)
        if clean:
            safeRemove(contaminated_sam)

    if(clean):
        safeRemove(Fastq_fw_trimmed)
    if(clean):
        safeRemove(Fastq_rv_trimmed)

    # Map against the barcodes
    mapFile = getTrToIdMap(withTr, ids, allowed_missed, allowed_kimera, s, l, e, statFile)

    if(clean):
        safeRemove(withTr)

    finish_exe_time = globaltime.getTimestamp()
    total_exe_time = finish_exe_time - start_exe_time

    # create json files with the results
    createDatabase(mapFile, lane_name, expName, statFile)

    if(clean):
        safeRemove(mapFile)

    print "Total Execution Time : " + str(total_exe_time)

    statFile.write("\nTotal Execution Time : " + str(total_exe_time) + "\n\n")

    #closing stats file
    statFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
