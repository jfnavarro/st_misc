#! /usr/bin/env python

import time
import datetime

class PipelineStats(object):
    """
    Represents an experiment stats
    """
    
    collectionname = "experiment.pipelinestats"
    oldlocationname = None
        
    @staticmethod
    def createStats(conn, experiment_id):
        ts = time.time()
        isodate = datetime.datetime.fromtimestamp(ts, None)
        coll = conn["experiment"]["pipelinestats"]
        post = { \
                "experiment_id": experiment_id, \
                "input_files": [None], \
                "output_files": [None], \
                "parameters": "Unknown", \
                "status": "COMPLETED", \
                "no_of_reads_mapped": -1, \
                "no_of_reads_annotated": -1, \
                "no_of_reads_mapped_with_find_indexes": -1, \
                "no_of_reads_contaminated": -1, \
                "no_of_barcodes_found": -1, \
                "no_of_genes_found": -1, \
                "no_of_transcripts_found": -1, \
                "no_of_reads_found": -1, \
                "mapper_tool": "Unknown", \
                "mapper_genome": "Unknown", \
                "annotation_tool": "Unknown", \
                "annotation_genome": "Unknown", \
                "quality_plots_file": "Unknown", \
                "log_file": "Unknown", \
                "doc_id": "Unknown", \
                "last_modified": isodate \
        }
        stats_id = coll.insert(post)
        coll.ensure_index("experiment_id", unique=True)
        return stats_id
    
    