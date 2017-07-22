#!/usr/bin/env python
import sys
import argparse
import os.path

import numpy as np
from skimage import transform as tf
from skimage import io
from st_toolbox.data import load_ndf
from st_toolbox.data import json_iterator

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Ellipse
from matplotlib.path import Path
from matplotlib import patches

import math
import itertools
from collections import defaultdict,Counter
import csv
import cjson


def main(args):
    #Load tissue image if required
    tissue = None
    newFilename = extractImageName(args.json)
    if args.visualize:
        tissue = io.imread(args.visualize)
        plotParams = {"DPI": args.dpi,
                      "xInches": (tissue.shape[1] / args.dpi),
                      "yInches": (tissue.shape[0] / args.dpi),
                      "tissue": tissue,
                      "single_cell": args.single_cell}

    elif not args.visualize_all is None:
        tissue = io.imread(args.visualize_all)
        plotParams = {"DPI": args.dpi, "xInches": (tissue.shape[1] / args.dpi), "yInches": (tissue.shape[0] / args.dpi), "tissue": tissue}

    #Read cells
    cellList = loadCells(args.cells)

    #Read transform
    mat = np.load(args.transform)
    st = tf.SimilarityTransform(matrix=mat)

    #Read expression data from JSON
    expression = np.zeros((1000, 1000), dtype=np.int)
    unique_events = defaultdict(Counter)
    it = json_iterator(args.json)
    for doc in it:
        expression[doc['x'], doc['y']] += doc['hits']
        unique_events[(doc['x'], doc['y'])][doc['gene']] += doc['hits']

    #Transform expression data to image coordinates
    e_x, e_y = expression.nonzero()
    e_crds = np.zeros((2, len(e_x)))
    e_crds[0, :] = e_x
    e_crds[1, :] = 499 - e_y
    t_e_crds = st.inverse(e_crds.T)
    
    #Define spill radius in terms of image pixels
    spillRadiusImg = getDiffusionRadiusInPixels(args.diffusion, st)
    
    if args.visualize_all:
        #Plot identified cells
        plotCells(args.output_folder+newFilename+"_1.png",plotParams, cellList)
    
    #Cluster cells, taking into account spill radius
    cellClusters = formCellClusters(cellList, spillRadiusImg)
    
    if args.visualize_all:
        #Plot clusters, no transcripts
        plotCellClusters(args.output_folder+newFilename+"_2.png",plotParams, cellClusters, spillRadiusImg)
        #Plot clusters and all transcripts
        plotCellClusters(args.output_folder+newFilename+"_3.png",plotParams, cellClusters, spillRadiusImg, t_e_crds)
    
    #Assign features to clusters
    feat_in_clusters = [ [] for x in range( len(cellClusters) ) ]
    feature_cluster_index = {}
    for idx,feature in enumerate(t_e_crds):
        for clust_idx,clust in enumerate(cellClusters):
            if feature_belongs_to_cluster(feature,clust,spillRadiusImg):
                feat_in_clusters[clust_idx].append( np.array( (e_x[idx],e_y[idx]) ))
                feature_cluster_index[ (e_x[idx],e_y[idx]) ] = clust_idx
    
    #New JSON filename = oldJSON_cells.json
    start_slice = args.json.rfind("/")
    start_slice = 0 if start_slice == -1 else start_slice+1
    newJson = args.output_folder+newFilename+"_cells.json"
    
    #Write annotated JSON file with cell cluster info
    writeAnnotatedJSON(args.json, newJson, cellClusters, feature_cluster_index)

    #Write cell cluster information to a file
    writeCellClusters(args.output_folder+newFilename+"_clusters.tsv", cellClusters)

    #Plot final visualization of the clustering + transcript assignment process
    if args.visualize or args.visualize_all:
        plotFinalImage(args.output_folder+newFilename+"_4.png", plotParams, cellClusters, feat_in_clusters, spillRadiusImg, st)
        if args.counts:
            plotFinalImage(args.output_folder+newFilename+"_4_counts.png", plotParams,cellClusters, feat_in_clusters,spillRadiusImg, st,"counts", unique_events)
        if args.unique_genes:
            plotFinalImage(args.output_folder+newFilename+"_4_uniquegenes.png", plotParams,cellClusters, feat_in_clusters,spillRadiusImg, st,"unique_genes", unique_events)


def extractImageName(image_path_with_extension):
    last_dash_index = image_path_with_extension.rfind('/')
    last_point_index = image_path_with_extension.rfind('.') #Assumes image always has extension

    last_dash_index += 1 #Ignores the / and if -1 sets  the var at 0 :D > micro math hack :D

    return image_path_with_extension[last_dash_index:last_point_index]


def loadCells(cell_filename):
    #Load cells from ImageJ plugin
    cellList = []
    with open(cell_filename,"r") as cellFile:
        csvreader = csv.reader(cellFile, delimiter="\t")
        for row in csvreader:
            x1 = float(row[1])
            y1 = float(row[2])
            diagX = int(row[3])
            diagY = int(row[4])
            #Center , radioX, radioY (ellipse)
            cellList.append(( np.array((x1,y1)), diagX, diagY, row[0]  ) )
        cellFile.close()
    return cellList


def getDiffusionRadiusInPixels(featureRadius, transform):
    #assumes applies for the diagonal radius
    neighbors = np.array([[0,0],[featureRadius,featureRadius]])
    neighbors_img = transform.inverse(neighbors)
    radiusImg = np.linalg.norm(neighbors_img[0]-neighbors_img[1])
    return radiusImg


def cells_overlap(c1,c2,spillRadiusImg):
    cell_distance = np.linalg.norm(c1[0]-c2[0]) #Euclidean distance
    sum_of_radiuses = max(c1[1],c1[2]) + max(c2[1],c2[2])
    #If distance between cells < sum of cell radiuses
    return cell_distance < sum_of_radiuses + (2* spillRadiusImg)
    
def cellInCluster(cell, clust, spillRadiusImg):
    for other_cell in clust:
        if cells_overlap(cell,other_cell,spillRadiusImg):
            return True
    return False

def formCellClusters(cellList,spillRadiusImg):
    cellClusters = [ ]
    for cell in cellList:
        tempClusters = []
        for idx,clust in enumerate(cellClusters):
            if cellInCluster(cell,clust,spillRadiusImg):
                tempClusters.append(idx)
        
        if len(tempClusters) == 0: #if cell does not belong to any cluster,
            cellClusters.append( [cell] ) #create new size 1 cluster with the cell
        else: 
            #Merge all clusters to which the cell belongs, remove old clusters and add the newly formed
            #tempClusters reversed, not to lose index,item association
            newCluster = list(itertools.chain.from_iterable( [cellClusters.pop(i) for i in reversed(tempClusters)]  ))
            newCluster.append(cell)
            cellClusters.append(newCluster)
    return cellClusters
    
def feature_in_cell(feature,cell,spillRadiusImg):
    #Euclidean distance
    distance = np.linalg.norm(cell[0]- feature)
    radius = max(cell[1],cell[2]) + spillRadiusImg
    return distance < radius

def feature_belongs_to_cluster(feature,cluster,spillRadiusImg):
    for cell in cluster:
        if feature_in_cell(feature,cell,spillRadiusImg):
            return True
    return False

#******************Output file functions***********************************
def writeCellClusters(outputFile, cellClusters):
    with open(outputFile,"w") as cellFile:
        cellFile.write("cell_id\tcenter_x\tcenter_y\taxis_x\taxis_y\tcluster_id\n")
        for clust_id, cluster in enumerate(cellClusters):
            for cell in cluster:
                cellFile.write(cell[3]+"\t"+str(cell[0][0])+"\t"+str(cell[0][1])+"\t"+str(cell[1])+"\t"+str(cell[2])+"\t"+str(clust_id)+"\n")
        cellFile.close()
        
def writeAnnotatedJSON(inputJson, outputJson, cellClusters, feature_cluster_index,filtered=False):
    #Write filtered reads to file
    originalFile = open(inputJson,"r")
    annotatedFile  = open(outputJson,"w")
    for line in originalFile:
        doc = cjson.decode(line)
        if (doc['x'],doc['y']) in feature_cluster_index:
            doc['cell_cluster_id']= feature_cluster_index[(doc['x'],doc['y'])]
            doc['cell_cluster_size']= len( cellClusters[ doc['cell_cluster_id']] )
            newLine = cjson.encode(doc)
            annotatedFile.write(newLine+"\n")
        elif not filtered:  
            annotatedFile.write(line)
    annotatedFile.close()

#***********************Plots!*****************************************
def plotCells(fileName, plotParams, cellList, spillRadiusImg=0  ):
    fig = plt.figure(figsize=(20,20))
    fig.set_size_inches(plotParams["xInches"], plotParams["yInches"])
    ax = fig.add_subplot(111)
    
    ax.imshow(plotParams["tissue"])
    #ax.scatter(t_e_crds[:, 0], t_e_crds[:, 1], c='pink', s=40, marker='s')
    #ax.scatter(transcripts[:, 0], transcripts[:, 1], c='pink', s=40, marker='s')
    for cell_it in cellList:   
        cell_item = Circle((cell_it[0][0],cell_it[0][1]), max(cell_it[1], cell_it[2])+spillRadiusImg, edgecolor="orange",lw=3,fill=False)
        ax.add_patch(cell_item)
    
    fig.savefig(fileName, dpi=plotParams["DPI"])
    plt.close()


def plotCellClusters(fileName, plotParams, cellClusters, spillRadiusImg, transcripts=None):
    clusterColors = itertools.cycle(["red", "green", "magenta", "yellow", "orange", "purple", "blue"])
    fig = plt.figure(figsize=(20, 20))
    fig.set_size_inches(plotParams["xInches"], plotParams["yInches"])
    ax = fig.add_subplot(111)

    ax.imshow(plotParams["tissue"])

    #Add transcripts
    if not transcripts is None:
        ax.scatter(transcripts[:, 0], transcripts[:, 1], c='pink', s=40, marker='s')

    #Add cells
    for cell_clust in cellClusters:
        if len(cell_clust) > 1:
            current_color = clusterColors.next()
        else:
            current_color = "cyan"  # Cyan for individual cells
        for cell_it in cell_clust:
            cell_item = Circle((cell_it[0][0], cell_it[0][1]), max(cell_it[1], cell_it[2]) + spillRadiusImg, edgecolor=current_color, lw=3, fill=False)
            ax.add_patch(cell_item)

    fig.savefig(fileName, dpi=plotParams["DPI"])
    plt.close()


def plotFinalImage(filename, plotParams, cellClusters, feat_in_clusters,
                   spillRadiusImg, transform, annot=None, unique_events=None):
    clusterColors = itertools.cycle(["red", "green", "magenta", "yellow", "orange", "purple", "blue"])

    #Deal with annotation
    if annot == "counts":
        annotate_fx = lambda feat, t_feat: plt.annotate(sum(unique_events[(feat[0], feat[1])].values()), t_feat[0], color='white', size=15)
    elif annot == "unique_genes":
        annotate_fx = lambda feat, t_feat: plt.annotate(len(unique_events[(feat[0], feat[1])]), t_feat[0], color='white', size=15)

    fig = plt.figure(figsize=(20, 20))
    fig.set_size_inches(plotParams["xInches"], plotParams["yInches"])
    ax = fig.add_subplot(111)
    ax.set_axis_off()

    ax.imshow(plotParams["tissue"])
    #Add only clusters with transcripts, and add transcript information
    for clust_idx, cell_clust in enumerate(cellClusters):
        #draw cells/clusters only if they have associated transcripts
        if len(feat_in_clusters[clust_idx]) > 0:
            if len(cell_clust) > 1:
                current_color = clusterColors.next()
                if plotParams['single_cell']:
                    continue
            else:
                current_color = "cyan"  # Cyan for individual cells

            for cell_it in cell_clust:
                cell_item = Circle((cell_it[0][0], cell_it[0][1]),
                                   max(cell_it[1], cell_it[2]) + spillRadiusImg,
                                   edgecolor=current_color, lw=3, fill=False)
                ax.add_patch(cell_item)

            #draw features belonging to cluster
            for feat in feat_in_clusters[clust_idx]:
                feat_cpy = np.array((feat[0], 499 - feat[1]))
                t_feat = transform.inverse(feat_cpy)
                ax.scatter(t_feat[0][0], t_feat[0][1], c=current_color, s=80, marker='s')
                if annot:
                    annotate_fx(feat, t_feat)

    fig.savefig(filename, dpi=plotParams["DPI"])
    plt.close()


def validate_args(args):
    if not os.path.isfile(args.json):
        sys.stderr.write("JSON file does not exist!\n")
        sys.exit(1)

    if not os.path.isfile(args.cells):
        sys.stderr.write("Image file does not exist!\n")
        sys.exit(1)

    if not os.path.isfile(args.transform):
        sys.stderr.write("Transform file does not exist!\n")
        sys.exit(1)

    if args.visualize and not os.path.isfile(args.visualize):
        sys.stderr.write("Image file does not exist!\n")
        sys.exit(1)

    if args.visualize_all and not os.path.isfile(args.visualize_all):
        sys.stderr.write("Image file does not exist!\n")
        sys.exit(1)

    if args.output_folder:
        args.output_folder = (args.output_folder if args.output_folder[-1] == "/" else args.output_folder+"/")
        if not os.path.isdir(args.output_folder):
            sys.stderr.write("Output directory does not exist!\n")
            sys.exit(1)
    return True

if __name__ == '__main__':
    #Turn off image display from matplotlib
    plt.ioff()
    #Process command line arguments
    parser = argparse.ArgumentParser(description="Overlays the json design reference on top of the image according to the transform")
    parser.add_argument("json",
                        help="JSON database file with gene expression levels for each barcode")
    parser.add_argument("transform",
                        help=".npy file with the appropiate coordinate transform between the image and the chip design")
    parser.add_argument("cells",
                        help=".tsv file with the enclosing cells as detected by the ST plugin for FIJI/ImageJ")

    parser.add_argument("-d", "--diffusion",
                        help="Define the expected transcript diffusion radius (in number of features). Default: 2",
                        default=2,type=int)
    parser.add_argument("-o", "--output-folder",
                        help="Folder where to output the results", default="./")
    parser.add_argument("--dpi",
                        help="Output image DPI. This should match the original images' DPI",
                        default=72)

    groupV = parser.add_mutually_exclusive_group()
    groupV.add_argument("-v", "--visualize",
                        help="Overlay the result of clustering and data integration on top of the provided image ",
                        metavar="tissue_image_file", default=None)
    groupV.add_argument("-V", "--visualize-all",
                        help="Create overlay images of the cell clustering and transcript assignment process and result",
                        metavar="tissue_image_file", default=None)

    # Visualization extras
    parser.add_argument("-u", "--unique-genes", action="store_true",
                        help="Plot additional final image annotating each feature with the number of unique genes it contains. Requires -v or -V.")
    parser.add_argument("-c", "--counts", action="store_true",
                        help="Plot additional final image annotating each feature with the number of reads it contatins. Requires -v or -V.")
    parser.add_argument("--single_cell", action="store_true",
                        help="Only plot clusters corresponding to singel cells. Requires -v or -V.",
                        default=False)

    args = parser.parse_args()

    if validate_args(args):
        main(args)
    else:
        sys.stderr.write("Invalid arguments. Exiting script")
        sys.exit(1)
