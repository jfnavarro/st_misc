## `compare_bc_edit_distance.py`

    usage: compare_bc_edit_distance.py [-h] ids_file mask_file json_file
    
    Script for comparing the Levenshtein edit distance between sequence and
    matched barcodes inside and outside a mask.
    
    positional arguments:
      ids_file    Barcode (id) definition file
      mask_file   File with stored mask in .npz format
      json_file   JSON-reads file
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `compare_T_content.py`

    usage: compare_T_content.py [-h] ids_file mask_file json_file
    
    Script for comparing the T content of reads inside and outside a mask.
    
    positional arguments:
      ids_file    Barcode (id) definition file
      mask_file   File with stored mask in .npz format
      json_file   JSON-reads file
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `find_coordinate_transform.py`

    usage: find_coordinate_transform.py [-h] [-r ROI] point_map
    
    Finds a transformation between image and array coordinate systems from a file
    with mapping between points stored a python dictionary.
    
    positional arguments:
      point_map          File with coordinate map dictionary, Must be a .txt file!
    
    optional arguments:
      -h, --help         show this help message and exit
      -r ROI, --roi ROI  Use Fiji ROI mode, provide a ROI list xls file as
                         argument.
    
## `find_polyt_binding_regions.py`

    usage: find_polyt_binding_regions.py [-h] [--bc_length BC_LENGTH]
                                         [--polyt_length POLYT_LENGTH] [--dry-run]
                                         fastq ref_index ref_name
    
    Small pipeline for finding regions in a reference dequence (Rn45s) which is
    mapped to by the poly-T region of reads in a formatted forward fastq file.
    
    positional arguments:
      fastq                 Formatted fastq file with fw reads.
      ref_index             Path to Bowtie2 index of reference sequence.
      ref_name              Name of reference region, e.g.
                            gi|374429539|ref|NR_046233.1| for Rn45s (as it appears
                            in the BT2 index
    
    optional arguments:
      -h, --help            show this help message and exit
      --bc_length BC_LENGTH
                            Barcode length
      --polyt_length POLYT_LENGTH
                            Poly-T region length
      --dry-run
    
## `genome_kmer_comparisons.py`

    usage: genome_kmer_comparisons.py [-h] [-k K] ribo genome
    
    Compare kmer profiles of genomes for given k
    
    positional arguments:
      ribo        ribo fasta file
      genome      genome fasta file
    
    optional arguments:
      -h, --help  show this help message and exit
      -k K        kmer length
    
## `json2scatter.py`

    usage: json2scatter.py [-h] [--highlight HIGHLIGHT] [--image IMAGE]
                           [--only-highlight]
                           json_file
    
    Script for creating a quality scatter plot from a json ST-data file. The
    output will be a .png file with the same name as the json file stored in the
    current directory. If a regular expression for a gene symbol to highlight is
    provided, the output image will be stored in a file called *.0.png. It is
    possible to give several regular expressions to highlight, by adding another
    --highlight parameter. The images from these queries will be stored in files
    with the number increasing: *.0.png, *.1.png, *.2.png, etc.
    
    positional arguments:
      json_file             JSON ST-data file
    
    optional arguments:
      -h, --help            show this help message and exit
      --highlight HIGHLIGHT
                            Regular expression for gene symbols to highlight in
                            the quality scatter plot. Can be given several times.
      --image IMAGE
      --only-highlight
    
## `json_barcode_splitter.py`

    usage: json_barcode_splitter.py [-h] [--out_ambiguous OUT_AMBIGUOUS]
                                    [--out OUT] [--cutoff CUTOFF]
                                    json_file
    
    Script for merging json ST-data files. It splits a json file containing
    barcodes into two (the one with ambiguous genes and the one without them) it
    allows to use a cut off of number of reads per transcript
    
    positional arguments:
      json_file             Json file with barcodes to be splitted.
    
    optional arguments:
      -h, --help            show this help message and exit
      --out_ambiguous OUT_AMBIGUOUS
                            Name of the outfile for barcodes with ambigous genes
      --out OUT             Name of the outfile for barcodes with no ambigous
                            genes
      --cutoff CUTOFF       Cut off of number of transcripts to filter
    
## `json_marked_stats.py`

    usage: json_marked_stats.py [-h] json_file mask_file
    
    Script for creating statistics and summary plots from a JSON ST-data file and
    a mask .npz file which discriminates features.
    
    positional arguments:
      json_file   JSON ST-data file
      mask_file   File with stored mask in .npz format
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `json_totsv.py`

    usage: json_totsv.py [-h] [-H] [-s char] [-f JSONdb] [-o OUTPUT] fields
    
    Extracts the selected fields from the JSONdb file and returns the values in a
    tab-separated file The command line utility reads input from STDIN and writes
    to STDOUT by default, but -f and -o options can be specified to read/write
    from/to a file respectively Fields to extract must be specified comma-
    separated with no spaces in between. A typical example would be the following:
    Extract the gene and position in chip from the barcodes.json file.
    json_totsv.py x,y,gene -f barcodes.json It is possible to pipe input and
    output to other utilities. Fore example, to a list all unique events ifor
    mitochondrial genes from a barcodes.json file cat barcodes.json | grep "MT_" |
    json_totsv.py x,y,gene | sort | uniq
    
    positional arguments:
      fields                Comma-separated names of the fields that will be
                            extracted from the jsondb
    
    optional arguments:
      -h, --help            show this help message and exit
      -H, --header          Add column headers to output
      -s char, --sep char   Field separator. Default is tab-character
      -f JSONdb, --file JSONdb
                            Read input from a JSONdb file
      -o OUTPUT, --output OUTPUT
                            Write output to file
    
## `json_unique.py`

    usage: json_unique.py [-h]
                          [--complement_files COMPLEMENT_FILES [COMPLEMENT_FILES ...]]
                          [-o OUT]
                          json_file
    
    Script for creating a JSON file with the unique events in a given JSON file
    compared to a given list of JSON files. E.g. to compare one hiseq lane to all
    the other lanes.
    
    positional arguments:
      json_file             First JSON file
    
    optional arguments:
      -h, --help            show this help message and exit
      --complement_files COMPLEMENT_FILES [COMPLEMENT_FILES ...]
                            Space seperated list of json ST files to compare the
                            first file with.
      -o OUT, --out OUT     Name of output file
    
## `json_xor.py`

    usage: json_xor.py [-h] [-o OUT] json_file_1 json_file_2
    
    Script for creating the symmetric difference (XOR) of two JSON files in terms
    of Unique Events.
    
    positional arguments:
      json_file_1        First JSON file
      json_file_2        Second JSON file
    
    optional arguments:
      -h, --help         show this help message and exit
      -o OUT, --out OUT  Name of output file
    
## `kmer_read_classifier.py`

    usage: kmer_read_classifier.py [-h] [--mode MODE] [--k K]
                                   [--overlap_cutoff OVERLAP_CUTOFF]
                                   reference fastq
    
    Simply classify reads using kmer profiles
    
    positional arguments:
      reference             reference fasta file
      fastq                 fastq file with reads to classify
    
    optional arguments:
      -h, --help            show this help message and exit
      --mode MODE           script mode, either "histogram" or "split"
      --k K                 kmer length, default 15
      --overlap_cutoff OVERLAP_CUTOFF
                            kmer overlap cutoff, default 20
    
## `make_script_documentation.py`

    usage: make_script_documentation.py [-h] scripts_directory doc_file
    
    This script goes through all scripts an generates a markdown file with the
    documentation for all of them.
    
    positional arguments:
      scripts_directory
      doc_file
    
    optional arguments:
      -h, --help         show this help message and exit
    
## `manual_feature_classification.py`

    usage: manual_feature_classification.py [-h] [--label LABEL]
                                            json_file out_suffix
    
    Use a lasso selection to label which features will be considered as under the
    tissue. This manual version of labeling should be used mostly to explore
    various comparisons between points. Label by drawing with left mouse key. To
    select more than one area, hold shift while selecting. To zoom the scatter
    plot, scroll. To pan the scatter plot, hold right mouse key. To save a labeled
    JSON file, hit the "s" key when selection is done. The output file will be
    stored in the working directory.
    
    positional arguments:
      json_file      JSON ST-data file
      out_suffix     Suffix for the .npz mask file which will contain the polygons
                     representing the marked regions.
    
    optional arguments:
      -h, --help     show this help message and exit
      --label LABEL  Name of label in this classification.
    
## `manual_image_registration.py`

    usage: manual_image_registration.py [-h] ndf_file out_file
    
    This script will show a region of the BORDER and ADDITIONAL_BORDER border
    points in a provided NDF Chip design file, and ask the user to relate the
    central marked point to a point in an an image in pixel coordinates. Typing in
    the coordinate (in the form e.g. 1300, 340) and hitting enter will relate the
    printed point to this given pixel point. To get a new point without
    registering the previous one (due to e.g. that region in the image begin
    occluded by tissue etc.) simply hit enter without typing anything.
    Additionaly, if one is using Fiji to store the registered point in the image
    as an ROI list, in stead of typing the point coordinate, type 'a' and hit
    enter to accept the point as being in the ROI list. When registration is done,
    type 'd' and hit enter to save files and also print out the registered points.
    
    positional arguments:
      ndf_file    NDF Chip design file
      out_file    Text file in to which the dict or list of registered points will
                  be written.
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `mapped_sam_fastq_filter.py`

    usage: mapped_sam_fastq_filter.py [-h] fastq sam out_fastq
    
    Takes a sam file with the original (single end) fastq file and filters out the
    reads from the original fastq file which are mapped.
    
    positional arguments:
      fastq       Original fastq file.
      sam         Mapped sam file.
      out_fastq   Name of filtered output fastq.
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `merge_json.py`

    usage: merge_json.py [-h] [-o OUT] json_files [json_files ...]
    
    Script for merging json ST-data files. The major point is to merge (feature,
    gene, expression) triples from several json files so that (f, g, e_1) + (f, g,
    e_2 ) = (f, g, e_1 + e_2).
    
    positional arguments:
      json_files         Space seperated list of json ST files to merge.
    
    optional arguments:
      -h, --help         show this help message and exit
      -o OUT, --out OUT  Name of merged output file
    
## `st_cells_data_integration.py`

    usage: st_cells_data_integration.py [-h] [-d DIFFUSION] [-o OUTPUT_FOLDER]
                                        [--dpi DPI]
                                        [-v tissue_image_file | -V tissue_image_file]
                                        [-u] [-c]
                                        json transform cells
    
    Overlays the json design reference on top of the image according to the
    transform
    
    positional arguments:
      json                  JSON database file with gene expression levels for
                            each barcode
      transform             .npy file with the appropiate coordinate transform
                            between the image and the chip design
      cells                 .tsv file with the enclosing cells as detected by the
                            ST plugin for FIJI/ImageJ
    
    optional arguments:
      -h, --help            show this help message and exit
      -d DIFFUSION, --diffusion DIFFUSION
                            Define the expected transcript diffusion radius (in
                            number of features). Default: 2
      -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                            Folder where to output the results
      --dpi DPI             Output image DPI. This should match the original
                            images' DPI
      -v tissue_image_file, --visualize tissue_image_file
                            Overlay the result of clustering and data integration
                            on top of the provided image
      -V tissue_image_file, --visualize-all tissue_image_file
                            Create overlay images of the cell clustering and
                            transcript assignment process and result
      -u, --unique-genes    Plot additional final image annotating each feature
                            with the number of unique genes it contains. Requires
                            -v or -V.
      -c, --counts          Plot additional final image annotating each feature
                            with the number of reads it contatins. Requires -v or
                            -V.
    
## `vennGeneExp.py`

    
    Modules/packages needed:
    matplotlib
    matplotlib_venn
    numpy
    
    Usage:
    vennGeneExp.py "name of experiment" <sample1_barcodes.json> "name of sample1" <sample2_barcodes.json> "name of sample2" minimum_TPM_cutoff maximum_TPM_cutoff correlation_coefficient
    
    minimum_TPM_cutoff:
    0 or a value < max
    
    maximum_TPM_cutoff:
    max or a value > 0
    
    correlation_coefficient:
    -P for Pearson's
    -S for Spearman's
    -B for both
    -N for none
    
    Output:
    1. Venn-diagram of overlapping genes and unique genes in each of the two samples
    2. Gene expression plot showing correlation between the two samples (only shared genes are plotted)
    3. A list with the calculated TPM for each gene in both samples. Note, if minimum_TPM_cutoff is set above 0, the genes with a lower value will be reported as TPM = 0
    4. A copy of what's written in the terminal (amount of transcripts in each sample etc)
    
    
## `view_ndf.py`

    usage: view_ndf.py [-h] ncf_file
    
    Graphically view an NCF chip design file
    
    positional arguments:
      ncf_file    NCF Chip design file
    
    optional arguments:
      -h, --help  show this help message and exit
    
## `visual_homography_estimator.py`
