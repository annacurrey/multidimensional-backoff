#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates LM for FLMs with multidimensional backoff (bigram with 3 clusters)
Usage: ./create-lm_2g3c.py training_file > output_file
Training file format: 
    - one sentence per line
    - words separated by space
    - words in the format W-word|S-small_cluster|L-large_cluster
    - assume small clusters are subsets of large clusters (i.e. given small know large)
    - also assume word-cluster mapping is 1-1

Output file format: 
    - similar to ARPA file format
    - cannot use traditional ARPA format because the backoffs are in a different dimension
    - TO DO more explanation

Created on Sun Mar 29 12:05:54 2015
Author: Anna Currey
"""

## TO DO ##
#  1. use simple Good-Turing for discounting
#  2. check probabilities sum to (near) 1
#  3. check input file format (and add info about it)
#  4. make the labels be a command-line argument or maybe detect them
#  5. update get_parts so it returns all parts (because I use them all)
#  6. maybe put all the bigrams into one dict
#  7. for now, forced small clusters to be subsets of large, but need to consider 
#     how it would work otherwise; backoff w-s and w-l? Consider s-l when the large
#     wasn't the large cluster of the word?
#  8. combine this with 3g2c
#  9. should I be using end of sentence markers?? (and beginning)
# 10. combine bigram and unigram helper functions
# 11. deal with undefined probabilities, backoffs
# 12. see utils for more to dos (checks to add, etc.)


from __future__ import division
from math import log
import argparse, utils, sys

__version__ = '1.3'

# variables for word, small cluster, and large cluster labels
WORD_LABEL = 'W'
SMALL_LABEL = 'S'
LARGE_LABEL = 'L'


#################################################################
######################### MAIN FUNCTION #########################
#################################################################

def main():
    ########## 0. parse command-line argument ##########
    # training file name only (required)
    parser = get_parser()
    args = vars(parser.parse_args())
    training_filename = args['training_file']
    
    
    ########## 1. get the unigram and bigram counts ##########
    ## need unigrams and bigrams for words and clusters
    # dictionaries to store the counts
    # format: {word0:{word1:count}}
    unigrams = {}
    small_clusters = {}
    large_clusters = {}
    bigrams_ww = {}
    bigrams_sw = {}
    bigrams_lw = {}
    
    # also get word factor files
    # convert from word to small cluster and small cluster to large cluster
    word_to_small = {}
    small_to_large = {}
    
    # will need total word count for unigram probs
    total_word_count = 0
    
    ## the ngram counts come from the training file
    with open(training_filename, 'r') as training_file:
        # read through line by line (one sentence per line)
        for line in training_file:
            # split the line into words (with clusters still attached)
            line_words = line.strip().split(' ')
            
            ## loop through the words in the sentence
            for index, word in enumerate(line_words):
                # increment total word count
                total_word_count += 1
                
                # get the word and its parts
                word2 = utils.get_part(word, WORD_LABEL)
                small2 = utils.get_part(word, SMALL_LABEL)
                large2 = utils.get_part(word, LARGE_LABEL)
                
                # add to mappings of words and factors
                utils.add_to_dict(word2, small2, word_to_small)
                utils.add_to_dict(small2, large2, small_to_large)
                
                # add to unigram count dictionaries
                utils.add_uni_counts(word2, unigrams)
                utils.add_uni_counts(small2, small_clusters)
                utils.add_uni_counts(large2, large_clusters)
                
                # if it is the second or later word, get prev word cluster
                # for first word, just consider unigrams (TO DO should be bigram with <s> first??)
                if index > 0:
                    word1 = utils.get_part(line_words[index-1], WORD_LABEL)
                    small1 = utils.get_part(line_words[index-1], SMALL_LABEL)
                    large1 = utils.get_part(line_words[index-1], LARGE_LABEL)
                    
                    # add to bigram dictionaries
                    utils.add_bi_counts(word1, word2, bigrams_ww)
                    utils.add_bi_counts(small1, word2, bigrams_sw)
                    utils.add_bi_counts(large1, word2, bigrams_lw)
    
    sys.stderr.write('Finished getting ngram count dictionaries\n')    
    
    ########## 3. calculate backoff probabilities for each ngram ##########
    ## get counts of counts for use in discounting
    count_unigrams = utils.get_counts_uni(unigrams)
    count_ww = utils.get_counts_bi(bigrams_ww)
    count_sw = utils.get_counts_bi(bigrams_sw)
    count_lw = utils.get_counts_bi(bigrams_lw)

    # will need vocab size for unk probs
    vocab_size = len(unigrams)
    sys.stderr.write('Finished getting counts of counts\n')    
    
    ## get discounts based on simple Good-Turing
    # TO DO later make this more robust so I can use other smoothing methods
    # note Good-Turing depends on the counts, not on the ngram itself
    disc_uni = utils.calc_discount(count_unigrams)
    disc_ww = utils.calc_discount(count_ww)
    disc_sw = utils.calc_discount(count_sw)
    disc_lw = utils.calc_discount(count_lw)
    
    ## calculate log probability of each unigram and bigram
    # dictionaries to store probabilities
    prob_unigrams = utils.probs_uni(unigrams, total_word_count, disc_uni)
    prob_ww = utils.probs_bi(bigrams_ww, unigrams, disc_ww)
    prob_sw = utils.probs_bi(bigrams_sw, small_clusters, disc_sw)
    prob_lw = utils.probs_bi(bigrams_lw, large_clusters, disc_lw)
    # TO DO where to store unk?
    # for now just make it a variable
    # unknowns (GT estimate): count(words appearing once) / |V| and store in variable
    prob_unk = log(count_unigrams[1], 10) - log(vocab_size, 10)

    sys.stderr.write('Finished getting probability dictionaries\n')    

    ########## 4. calculate backoff (alpha) of each backoff step ##########
    # backoff from word to small cluster
    backoff_ws = utils.calc_backoff_bi(word_to_small, prob_ww, prob_sw)
    sys.stderr.write('Finished getting w2s backoff dictionary\n')   
    
    # backoff from small cluster to large cluster
    backoff_sl = utils.calc_backoff_bi(small_to_large, prob_sw, prob_lw)
    sys.stderr.write('Finished getting s2l backoff dictionary\n')  
    ## TO DO some of these (and w2s) are > 1 which shouldn't happen!
    
    # backoff from large cluster to unigram (ignore previous word altogether)
    backoff_l = utils.calc_backoff_uni(prob_lw, prob_unigrams)
    #### TO DO Something is wrong here because almost all are -1000!

    sys.stderr.write('Finished getting l2u backoff dictionary\n')   
    sys.stderr.write('Finished getting backoff factor dictionaries\n')    
    

    ########## 5. print probs and alphas to stdout ##########
    ## probabilities
    # start with unknown prob
    sys.stdout.write('\unks:\n')
    sys.stdout.write(str(prob_unk) + '\t<unk>\n')
    
    # unigram probs
    sys.stdout.write('\\1-grams:\n')
    for unigram in prob_unigrams:
        sys.stdout.write(str(prob_unigrams[unigram]) + '\t' + unigram + '\n')
    
    # lw bigram probs
    sys.stdout.write('\\2-grams lw:\n')
    for large_cluster in prob_lw:
        for word in prob_lw[large_cluster]:
            sys.stdout.write(str(prob_lw[large_cluster][word]) + '\t' + large_cluster + ' ' + word + '\n')
    
    # sw bigram probs
    sys.stdout.write('\\2-grams sw:\n')
    for small_cluster in prob_sw:
        for word in prob_sw[small_cluster]:
            sys.stdout.write(str(prob_sw[small_cluster][word]) + '\t' + small_cluster + ' ' + word + '\n')
    
    # ww bigram probs
    sys.stdout.write('\\2-grams ww:\n')
    for prev_word in prob_ww:
        for word in prob_ww[prev_word]:
            sys.stdout.write(str(prob_ww[prev_word][word]) + '\t' + prev_word + ' ' + word + '\n')
    
    ## backoff weights
    # back off from lw to unigram
    sys.stdout.write('\\backoff l to unigram:\n')
    for cluster in backoff_l:
        sys.stdout.write(str(backoff_l[cluster]) + '\t' + cluster + '\n')
    
    # backoff from sw to lw
    sys.stdout.write('\\backoff s to l:\n')
    for cluster in backoff_sl:
        sys.stdout.write(str(backoff_sl[cluster]) + '\t' + cluster + '\n')
    
    # backoff from ww to sw
    sys.stdout.write('\\backoff w to s:\n')
    for cluster in backoff_ws:
        sys.stdout.write(str(backoff_ws[cluster]) + '\t' + cluster + '\n')




####################################################################
######################### HELPER FUNCTIONS #########################
####################################################################

## parsing command-line arguments
def get_parser():
    parser = argparse.ArgumentParser()
    
    # training data file (required argument)
    parser.add_argument('training_file', help='file containing training data', 
                        metavar='training_file', type=str)
    # version info (optional)
    parser.add_argument('-v', '--version', help='displays current version', 
                        action='version', version='%(prog)s '+__version__)
    
    return parser




####################################################################
######################### EXECUTE THE CODE #########################
####################################################################

if __name__ == '__main__':
    main()

