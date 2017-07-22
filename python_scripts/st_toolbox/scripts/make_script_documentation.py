""" This script goes through all scripts an generates a markdown file with the
documentation for all of them.
"""
import argparse
from glob import glob
import os
import subprocess


def main(args):
    doc_file = open(args.doc_file, 'w')
    scripts = glob(args.scripts_directory + '*.py')
    for script in scripts:
        script = os.path.basename(script)
        doc_file.write('## `' + script + '`\n')
        outp = subprocess.check_output([script, '-h'])
        outp = '\n    ' + outp.replace('\n', '\n    ')
        doc_file.write(outp + '\n')

    doc_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scripts_directory', type=str)
    parser.add_argument('doc_file', type=str)
    args = parser.parse_args()
    main(args)
