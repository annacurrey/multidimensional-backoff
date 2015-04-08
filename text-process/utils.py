# -*- coding: utf-8 -*-
"""
Helper functions for text processing in preparation for running MDB LMs

Created on Wed Apr  8 21:31:09 2015
@author: annacurrey
"""
import sys

## read in factor file and store it in a dictionary
# input: name of the file containing the clusters
# output: dictionary {word:cluster}
def get_cluster_dict(filename, cluster_delim):
    # dictionary to store factors
    factor_dict = {}
    
    # open the file
    with open(filename, 'r') as factor_file:
        # read through line by line
        for line in factor_file:
            # split word from factor (line format: word factor)
            split_line = line.strip().split(cluster_delim)
            
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


