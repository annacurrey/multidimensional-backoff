#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adds two sets of factors to a data set for use in a factored language model
Usage: ./add-factors.py [infile] [factor1] [label1] [factor2] [label2] > outfile

Input: * data file to which factors should be added
               - one sentence per line
               - words separated by spaces
               - no additional tags
        * file containing the first set of factors
               - one word per line
               - format: "[word] [factor label]"
        * label for the first set of factors (one letter)
        * file containing the second set of factors (same format as other factors file)
               (map from first set to second set)
        * label for the second set of factors
        * desired outfile name
 
Output: file identical to infile, except that factors have been added
         words are of the format: W-word|A-factor1|B-factor2 (A and B factor labels)

Created on Wed Apr  8 21:24:12 2015
Author: Anna Currey
"""

## TO DO ##
#  1. allow input of any number of factors (currently just 2)
#  2. allow factors to be based on either word or other factors 
#     (currently small factors based on word, large based on small)
#  3. cluster labels may have to be one letter for FLMs; if so, enforce that
#  4. improve argument checking (especially infile)
#  5. consider making arguments positional
#  6. don't hard-code word label (may not always want 'W')


import argparse, sys, utils

__version__ = '1.2'


## outfile formatting variables
WORD_DELIM = ' '
SENT_DELIM = '\n'
FACTOR_DELIM = '|'
FACTOR_WORD = '-'
WORD_LABEL  = 'W'

## formatting of cluster files
CLUSTER_DELIM = ' '


## main function
def main():
    ## parse command-line arguments
    parser = get_parser()
    args = vars(parser.parse_args())
    
    # name of the infile (required argument)
    infile_name = args['infile']
    
    # factor file 1 (required argument)
    factor1_name = args['factor1']
    
    # factor label 1 (required argument)
    label1 = args['label1']
    
    # factor file 2 (required argument)
    factor2_name = args['factor2']
    
    # factor label 2 (required argument)
    label2 = args['label2']
    
    
    ## read the factor files and store them in a dictionary
    factor1_dict = utils.get_factor_dict(factor1_name, CLUSTER_DELIM)
    factor2_dict = utils.get_factor_dict(factor2_name, CLUSTER_DELIM)

    
    ## now go through the infile and add factors
    # format is W-word|A-factor1|B-factor2
    with open(infile_name, 'r') as infile:
        # read in line by line (one line is a sentence)
        for line in infile:
            # separate out words
            words = line.strip().split(WORD_DELIM)
            # this is where we will be adding factors
            sentence = []
            # add each factor to each word
            for word in words:
                # get the factor
                # if word has no factor, use factor -1
                word_factor1 = factor1_dict[word] if word in factor1_dict else '-1'
                word_factor2 = factor2_dict[factor1_dict[word]] if word in factor1_dict else '-1'
                # add factor in correct format
                sentence.append(WORD_LABEL + FACTOR_WORD + word + FACTOR_DELIM + 
                                label1 + FACTOR_WORD + word_factor1 + FACTOR_DELIM + 
                                label2 + FACTOR_WORD + word_factor2)
            
            # now that we have our sentence, can write to output
            for word in sentence:
                sys.stdout.write(word + WORD_DELIM)
            # need a new line to separate sentence
            sys.stdout.write(SENT_DELIM)
            

## parse command-line arguments
def get_parser():
    parser = argparse.ArgumentParser()
    
    # infile name (required argument)
    parser.add_argument('infile', help='file with data to which factors will be added', 
                        metavar='infile', type=str)
    # factor file 1 (required argument)
    parser.add_argument('factor1', help='file containing first factor', 
                        metavar='factor1', type=str)
    # factor label 1 (required argument)
    parser.add_argument('label1', help='label for the first factor', 
                        metavar='label1', type=str)
    # factor file 2 (required argument)
    parser.add_argument('factor2', help='file containing second factor', 
                        metavar='factor2', type=str)
    # factor label 2 (required argument)
    parser.add_argument('label2', help='label for the second factor', 
                        metavar='label2', type=str)
    
    # version info (optional)
    parser.add_argument('-v', '--version', help='displays current version', 
                        action='version', version='%(prog)s '+__version__)
    
    return parser


## execute the code
if __name__ == '__main__':
    main()