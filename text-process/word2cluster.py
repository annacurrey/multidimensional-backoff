#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Replaces words in a file with their corresponding clusters
Usage: ./word2cluster.py infile clusterfile > outfile

Input file format: 
    - one sentence per line
    - words separated by spaces

Cluster file format: 
    - one word per line
    - line format: word cluster
    - no other information in file
    - one cluster per word

Output file format: 
    - identical to input file, but words replaced with their clusters
    - words without clusters are not replaced
    - note we don't replace unclustered words with -1 here because we don't 
      want them to cluster with other words if we run word2vec again

Created on Mon Mar 30 13:39:51 2015
Author: Anna Currey
"""

## TO DO ##
#  1. infile checking

import argparse
import sys

__version__ = '1.1'

## variables according to infile format and cluster file format
WORD_DELIM = ' '
SENT_DELIM = '\n'
CLUSTER_DELIM = ' '

## main function
def main():
    ## parse command-line arguments
    parser = get_parser()
    args = vars(parser.parse_args())
    
    # name of the infile (required argument)
    infile_name = args['infile']
    
    # name of the cluster file (required argument)
    cluster_name = args['cluster_file']


    ## read the factor files and store them in a dictionary
    cluster_dict = get_cluster_dict(cluster_name)


    ## now go through the infile replace word with cluster
    with open(infile_name, 'r') as infile:
        # read in line by line (one line is a sentence)
        for line in infile:
            # separate out words
            words = line.strip().split(WORD_DELIM)
            # this is where we will be adding factors
            sentence = []
            # add each factor to each word
            for word in words:
                # if word has no cluster, use the word itself
                word_cluster = cluster_dict[word] if word in cluster_dict else word
                sentence.append(word_cluster)
            # now that we have our sentence, can write to outfile
            for word in sentence:
                sys.stdout.write(word + WORD_DELIM)
            # need a new line to separate sentence
            sys.stdout.write(SENT_DELIM)


## read in factor file and store it in a dictionary
# input: name of the file containing the clusters
# output: dictionary {word:cluster}
def get_cluster_dict(filename):
    # dictionary to store factors
    factor_dict = {}
    
    # open the file
    with open(filename, 'r') as factor_file:
        # read through line by line
        for line in factor_file:
            # split word from factor (line format: word factor)
            split_line = line.strip().split(CLUSTER_DELIM)
            
            # check the file
            # line should consist only of word and factor!
            if len(split_line) != 2:
                sys.stderr.write('Cluster file ' + filename + ' not in correct format\n')
                sys.stderr.write('Line contains ' + len(split_line) + ' parts\n')
                sys.exit(1)
            # word should not appear twice in factor file!
            if split_line[0] in factor_dict:
                sys.stderr.write('Cluster file ' + filename + ' not in correct format\n')
                sys.stderr.write('Word ' + split_line[0] + ' appears more than once\n')
                sys.exit(2)
            
            # add the word and its factor to the dictionary
            factor_dict[split_line[0]] = split_line[1]
    
    return factor_dict


## parsing command-line arguments
def get_parser():
    parser = argparse.ArgumentParser()
    
    # infile name (required argument)
    parser.add_argument('infile', help='file with data to which factors will be added', 
                        metavar='infile', type=str)
    # factor file 1 (required argument)
    parser.add_argument('cluster_file', help='file containing clusters', 
                        metavar='cluster_file', type=str)
    # version info (optional)
    parser.add_argument('-v', '--version', help='displays current version', 
                        action='version', version='%(prog)s '+__version__)
    
    return parser


## execute the code
if __name__ == '__main__':
    main()