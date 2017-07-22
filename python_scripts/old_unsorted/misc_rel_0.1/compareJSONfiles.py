#! /usr/bin/env python
# @Created by Zinat Sultana


import getopt
import sys
import json
import csv

def usage():
    print 'python compareJSONfiles.py  input1.json  input2.json'

def stripExtension(string):
    f = string.rsplit('.', 1)
    '''
    #this part is taken from Jose to create the intermideary files into the
    #working folder
    if(f[0].find("/") != -1):
        return f[0].rsplit('/', 1)[1]
    else:
        return f[0]
    '''
    return f[0]
def sortList(FileToSort):

    File_sort_out = stripExtension(FileToSort)+ "_sort.json"
    list_sort = []
    filea = open(FileToSort, 'r')

    #put lines into list
    for line in filea:
       list_sort.append((line))
    filea.close()

    #sort list
    list_sort.sort()

    #open a new file and save the sorted lines to that file
    fout=open(File_sort_out,"w")

    for item in list_sort:
        fout.writelines(item)

    print "Done Sorting"
    return File_sort_out

def compareTranscripts(json_file1,json_file2):

    #Store the transcripts which do not match with the new pipeline output
    # to out_diff_old and out_diff_new
    out_diff_json1 = stripExtension(json_file1)+ "_diff.txt"
    out_diff_json2 = stripExtension(json_file2)+ "_diff.txt"

    

    #matches transcripts from old_sort and new_sort into out_sim
    out_sim = stripExtension(json_file1)+ "_sim.txt"
    
    
    #statistics about the how many matches or not
    out_stat = stripExtension(json_file1)+ "_stat.txt"
    
    #input files
    inF1 = file(json_file1, "r")
    inF2 = file(json_file2, "r")


    #out Files
    out_dif_o = file(out_diff_json1, "w")
    out_dif_n = file(out_diff_json2, "w")
    out_s = file(out_sim, "w")
    outF_stat = file(out_stat,"w")


    num_diff=0
    num_siml=0

    while(True):

        str1_old_sort = inF1.readline()
        str2_new_sort = inF2.readline()

        if str1_old_sort!=str2_new_sort:
            
            num_diff=num_diff+1

            out_dif_n.writelines(str2_new_sort)
            out_dif_o.writelines(str1_old_sort)

        if str1_old_sort==str2_new_sort:
            out_s.writelines(str2_new_sort)
            num_siml=num_siml+1
        if not str1_old_sort:
            break;

    outF_stat.write("Diff : "+str(num_diff))
    outF_stat.write("\nSim : "+str(num_siml))
    print "Diff:",num_diff
    print "Siml:",num_siml
    print "Done Comparing"
    


def get_IdGeXYNr_column(file_sort):


    first_col=[]
    
    s_file=open(file_sort,"r")

    IdGeXYNr_cols   = stripExtension(file_sort)+ "_IdGeXYNr.txt"
    inf = open(IdGeXYNr_cols,"w")

    
    for stringNotMatch in s_file:

        

        first_col.append(stringNotMatch.split(',')[0].strip())
        c=first_col[0].rstrip().split('{')[1].strip()
        
        inf.writelines(first_col[0].rstrip().split('{')[1].strip()+"\t")


        #take id, gene , x and y and Nr of gene
        for i in range(1,5):
            
            inf.writelines(stringNotMatch.rstrip().split(',')[i].strip()+"\t")
        inf.writelines("\n")
        
        
        #reset first_col
        for item in first_col:
            first_col.pop()
        
        
    
    return IdGeXYNr_cols

def main(json_file1,json_file2):

    #sort two json files
    json_file_sort1=sortList(json_file1)
    json_file_sort2=sortList(json_file2)

    
    #get Id , gene , Nr of gene , x and y cordinates from sorted JSON1
    json_col1 =get_IdGeXYNr_column(json_file_sort1)

    #get Id , gene , Nr of gene , x and y cordinates from sorted JSON2
    json_col2 =get_IdGeXYNr_column(json_file_sort2)


    #compare two json files
    compareTranscripts(json_col1,json_col2)



    print "end comparing"


if __name__ == "__main__":

    if len(sys.argv)!=3:
            usage()
            sys.exit(1)
    main(sys.argv[1],sys.argv[2])
