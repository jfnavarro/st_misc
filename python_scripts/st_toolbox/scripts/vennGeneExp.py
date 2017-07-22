#!/usr/bin/env python
 
#Script made by Fredrik Salmen
import sys

#Help and usage
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print '\nModules/packages needed:'
  print 'matplotlib'
  print 'matplotlib_venn' 
  print 'numpy\n'
  print 'Usage:'
  print 'vennGeneExp.py "name of experiment" <sample1_barcodes.json> "name of sample1" <sample2_barcodes.json> "name of sample2" minimum_TPM_cutoff maximum_TPM_cutoff correlation_coefficient\n'
  print 'minimum_TPM_cutoff:' 
  print '0 or a value < max\n' 
  print 'maximum_TPM_cutoff:'
  print 'max or a value > 0\n'
  print 'correlation_coefficient:'
  print '-P for Pearson\'s'
  print '-S for Spearman\'s'
  print '-B for both'
  print '-N for none\n'
  print 'Output:' 
  print '1. Venn-diagram of overlapping genes and unique genes in each of the two samples'
  print '2. Gene expression plot showing correlation between the two samples (only shared genes are plotted)'
  print '3. A list with the calculated TPM for each gene in both samples. Note, if minimum_TPM_cutoff is set above 0, the genes with a lower value will be reported as TPM = 0'
  print '4. A copy of what\'s written in the terminal (amount of transcripts in each sample etc)\n' 
  exit()

#importing modules and packages
print 'Importing modules and packages'
overstats = 'Importing modules and packages\n'

from collections import defaultdict
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from matplotlib import pyplot as plt
import pylab
from matplotlib_venn import venn2
import numpy as np
import math
import json 

print 'Analysis started'
overstats += 'Analysis started\n'

print 'Step 1 of 6: Reading and storing data from input files'
overstats += 'Step 1 of 6: Reading data from input files\n'

#Input/output files and parameters
extitle = sys.argv[1]
name1 = sys.argv[3]
name2 = sys.argv[5]
lines1 = open(sys.argv[2], 'r').readlines()
lines2 = open(sys.argv[4], 'r').readlines()
minvalue = sys.argv[6]
maxvalue = sys.argv[7]

exrp = extitle.replace(' ', '_')
exrp = exrp.replace(':', '_')
outover = open(exrp + '_terminal.txt', 'w')
outcomp = open(exrp + '_gene_expression_list_TPM.txt', 'w')
 
hgenes = defaultdict(lambda: [0,0])
genelist = 'Gene\t' + name1 + '\t' + name2 + '\n' 
x = []
y = []
xlog = []
ylog = []
xtot = 0
ytot = 0
scount1 = 0
scount2 = 0
scount12 = 0

#Loop over each line in the two sample files, extracts gene name and number of transcripts and stores them in a dictionary
for line1 in lines1:
  jdata1 = json.loads(line1)
  hgenes[jdata1['gene']][0] += int(jdata1['hits'])
  hgenes[jdata1['gene']][1] += 0
  xtot += int(jdata1['hits'])

for line2 in lines2:
  jdata2 = json.loads(line2)
  hgenes[jdata2['gene']][1] += int(jdata2['hits'])
  hgenes[jdata2['gene']][0] += 0
  ytot += int(jdata2['hits'])

#Setting min- and maxvalue
recminx = 10e5 / xtot
recminy = 10e5 / ytot

if maxvalue == '0':
  print 'Error! Please set the maximum allowed expression to a value above 0!'
  exit()
if minvalue == 'min':
  if recminx > recminy:
    minvalue = recminx
  else:
    minvalue = recminy
if maxvalue == 'max':
  maxvalue = 0

minvalue = float(minvalue)
maxvalue = float(maxvalue)

if minvalue < 0:
  print 'Error! Negative minimum expression value is not allowed!'
  exit()
if maxvalue < 0:
  print 'Error! Negative maximum expression value is not allowed!'
  exit()

print 'Step 2 of 6: Normalizing data to "Tags/Transcripts Per Million mapped (TPM)"'
overstats += 'Step 2 of 6: Normalizing data to "Tags/Transcripts Per Million mapped (TPM)"\n'

#Loop to calculate TPM                                                                                                                                                    
for key, value in hgenes.iteritems():                                                                                                                                                               
  value[0] = (value[0] * 10e5) / xtot
  value[1] = (value[1] * 10e5) / ytot

#Removes low and high expressed genes at the cutoffs (TPM) of choice 
  if value[0] < minvalue:
    value[0] = 0.0
  if value[1] < minvalue:
    value[1] = 0.0

  if maxvalue > 0:                                                                                                                                                                                              
    if value[0] > maxvalue:                                                                                                                                                                                     
      value[0] = 0.0                                                                                                                                                                                      
      value[1] = 0.0                                                                                                                                                                                 
    if value[1] > maxvalue:                                                                                                                                                                                     
      value[0] = 0.0                                                                                                                                                                                        
      value[1] = 0.0 

if maxvalue == 0:
  maxvalue = 'max'

print 'Step 3 of 6: Calculating gene overlap and expression (only genes with an expression of ' + str(minvalue) + ' - ' + str(maxvalue) + ' TPM)'
overstats += 'Step 3 of 6: Calculating gene overlap and expression (only genes with an expression of ' + str(minvalue) + ' - ' + str(maxvalue) + ' TPM)\n'

#Loop to generate a string with the gene names and the expression in each sample
for key, value in hgenes.iteritems():

#Creating two lists based on the expression in each sample 
  if value[0] and value[1] != 0:
    logx = math.log(value[0], 10)
    logy = math.log(value[1], 10)
    xlog.append(logx)
    ylog.append(logy)
    x.append(value[0])
    y.append(value[1])
  if value[0] or value[1] != 0:
    genelist += key + '\t' + str(value[0]) + '\t' + str(value[1]) + '\n'

#Counter for overlapping genes in both samples
  if value[0] == 0 and value[1] != 0:
    scount2 += 1
  if value[0] and value[1] != 0:
    scount12 += 1
  if value[0] != 0 and value[1] == 0:
    scount1 += 1

#Calculation of parameters for the results
scounttot = scount1 + scount2 + scount12
q1 = '%.1f' % (100 * (float(scount1)/float(scounttot)))
q2 = '%.1f' % (100 * (float(scount2)/float(scounttot)))
q12 = '%.1f' % (100 * (float(scount12)/float(scounttot)))

print 'Step 4 of 6: Printing stats'
overstats += 'Step 4 of 6: Printing stats\n'

#Writes results to files and terminal
outcomp.write(genelist)
outcomp.close()

print '\n\t"' + name1 + '" contains ' + str(xtot) + ' transcripts'
print '\t"' + name2 + '" contains ' + str(ytot) + ' transcripts'
print '\n\tGenes unique for "' + name1 + '":\t\t' + str(scount1) +' (' + str(q1) + '%)' 
print '\tGenes unique for "' + name2 + '":\t\t' + str(scount2) +' (' + str(q2) + '%)'
print '\tGenes shared by "' + name1 + '" and "' + name2 + '":\t' + str(scount12) +' (' + str(q12) + '%)\n' 
overstats += '\n\t"' + name1 + '" contains ' + str(xtot) + ' transcripts\n'
overstats += '\t"' + name2 + '" contains ' + str(ytot) + ' transcripts\n'
overstats += '\n\tGenes unique for "' + name1 + '":\t\t' + str(scount1) +' (' + str(q1) + '%)\n'
overstats += '\tGenes unique for "' + name2 + '":\t\t' + str(scount2) +' (' + str(q2) + '%)\n' 
overstats += '\tGenes shared by "' + name1 + '" and "' + name2 + '":\t' + str(scount12) +' (' + str(q12) + '%)\n\n'

#Calculations for correalation
rp = pearsonr(xlog, ylog)
rs = spearmanr(xlog, ylog)
rp0 = '%.3f' % (rp[0])
rs0 = '%.3f' % (rs[0])
ly = 0.95

#Option to choose which correlation coefficient to be printed
if sys.argv[8] == '-P':
  corr = 'Pearson\'s Correlation Coefficient: r = ' + str(rp0)
elif sys.argv[8] == '-S':
  corr = 'Spearman\'s Correlation Coefficient: r = ' + str(rs0)
elif sys.argv[8] == '-B':
  corr = 'Pearson\'s Correlation Coefficient: r = ' + str(rp0) + '\nSpearman\'s Correlation Coefficient: r = ' + str(rs0)
  ly = 0.925
elif sys.argv[8] == '-N':
  corr = ''
else:
  print 'Error! No existing parameter for correlation calculation has been selected. Please use -P for Pearson\'s, -S for Spearman\'s, -B for both, or -N for none!'
  exit()

print 'Step 5 of 6: Generating Venn diagram'
overstats += 'Step 5 of 6: Generating Venn diagram\n'

#Generate Venn diagram                                                                                                                                                                                          
plt.figure(figsize = (10, 10))
plt.title('Venn diagram: ' + extitle)
v = venn2(subsets = (scount1, scount2, scount12), set_labels = ('', ''))
v.get_patch_by_id('11').set_color('purple')
v.get_patch_by_id('01').set_color('blue')
plt.legend(('unique genes for "' + name1 + '" (' + q1 + '%)', 'unique genes for "' + name2 + '" (' + q2 + '%)', 'shared genes (' + q12 + '%)'), loc = 'upper center', bbox_to_anchor = (0.475, 0.065))
plt.savefig(exrp + '_venn_diagram.png')
plt.show()

print 'Step 6 of 6: Generating gene expression plot (only shared genes plotted)'
overstats += 'Step 6 of 6: Generating gene expression plot (only shared genes plotted)\n'

#Generates gene expression plot
fig = plt.figure(figsize = (10.3, 10))
ax = fig.add_subplot(1, 1, 1)
plt.title('Gene expression: ' + extitle)
plt.xlabel('"' + name1 + '" (TPM)')
plt.ylabel('"' + name2 + '" (TPM)')
plt.scatter(x, y, s = 5)
ax.set_xscale('log')
ax.set_yscale('log')
plt.xlim(minvalue, 10e4)
plt.ylim(minvalue, 10e4)
plt.text(0.05, ly, corr, transform = ax.transAxes)
plt.savefig(exrp + '_gene_expression_plot.png')
plt.show()

print 'Analysis finished'
overstats += 'Analysis finished'
outover.write(overstats)
outover.close()



