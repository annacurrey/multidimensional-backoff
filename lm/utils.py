# -*- coding: utf-8 -*-
"""
Helper functions for multidimensional backoff LMs and query

Created on Mon Apr  6 19:06:14 2015
Author: Anna Currey
"""
from __future__ import division
import sys
from math import log


## updates the counts in a bigram count dictionary
# input: bigram and dictionary (format: {word1:{word2:count}})
# output: none (dictionary modified)
# TO DO later combine this with add uni counts
def add_bi_counts(word1, word2, dictionary):
    # if the first word of bigram in dictionary
    if word1 in dictionary:
        # update counts for dictionary of that word
        add_uni_counts(word2, dictionary[word1])
    # otherwise, add the bigram to the dictionary
    else:
        dictionary[word1] = {word2:1}
    return

      
## adds a key-value pair to a dictionary if it's not already there
## I believe this is equivalent to collections.defaultdict
## note does not overwrite -- error message if key exists with different value
# input: key, value, dictionary to update
# output: none (dictionary modified)
def add_to_dict(key, value, dictionary):
    # if the key is there, don't overwrite
    if key in dictionary:
        # error if key exists with different value
        if dictionary[key] != value:
            sys.stderr.write('Attempting to overwrite existing key-value pair\n')
            sys.stderr.write('Dict: ' + dictionary)
            sys.stderr.write(' Key: ' + key + ' Value: ' + value + '\n')
            sys.exit(1)
        else: 
            return 0
    # if key not there, update dictionary
    else:
        dictionary[key] = value
        return 0


## updates the counts in a unigram count dictionary
# input: key and dictionary
# output: none (dictionary modified) 
def add_uni_counts(key, dictionary):
    # add one to counts if key in dictionary
    if key in dictionary:
        dictionary[key] += 1
    # otherwise add the key to the dictionary
    else:
        # seen it once, so count is one
        dictionary[key] = 1
    return 0


## calculates backoff weights for backing off to small or large cluster
# input: mapping of the previous cluster to the current cluster (one backing off to)
#        probability dictionary of the cluster backing off to
#        probability dictionary of the cluster backing off from
# output: dictionary mapping word/cluster to backoff weights
# TO DO later combine with calc_backoff_uni
def calc_backoff_bi(p2c_mapping, prev_bigram_counts, curr_bigram_counts):
    # mapping from prev cluster to backoff weights (since curr probs fcn of prev)
    backoff_weights = {}
    # for each more informative cluster ('previous' cluster)
    for prev_cluster in prev_bigram_counts:
        # find the less informative cluster ('current' cluster)
        # note should be in the mapping since it was derived from training data
        curr_cluster = p2c_mapping[prev_cluster]
        # keep track of probs
        prev_prob = 0
        curr_prob = 0
        # loop through each word2 that follows the prev cluster
        for word2 in prev_bigram_counts[prev_cluster]:
            # add the prev prob (for numerator) -- note NOT log prob
            prev_prob += 10 ** prev_bigram_counts[prev_cluster][word2]
            # add curr prob (for denominator) -- also NOT log prob
            # note don't need to worry about backoff
            # if the ww bigram appears, then sw appears so no need to consider lw, etc.
            curr_prob += 10 ** curr_bigram_counts[curr_cluster][word2]
            # now add to dict
            # TO DO need to deal with when it is zero/undefined
            backoff_weights[prev_cluster] = log(1-prev_prob, 10) - log(1-curr_prob, 10)
    
    return backoff_weights


## calculates backoff weights for backing off from long cluster to unigrams
# input: list of long clusters
#        probability dictionary of the unigrams
#        probability dictionary of the cluster backing off from (long cluster)
# output: dictionary mapping large cluster to backoff weights
# TO DO maybe combine this with calc_backoff_bi
def calc_backoff_uni(cluster_list, prev_dict, curr_dict):
    # map from large cluster to backoff weights
    backoff_weights = {}
    # for each large cluster
    for cluster in prev_dict:
        # keep track of probs
        prev_prob = 0
        curr_prob = 0
        # loop through each word2 that follows the cluster
        for word2 in prev_dict[cluster]:
            # add the prev prob (for numerator) -- note NOT log prob
            prev_prob += 10 ** prev_dict[cluster][word2]
            # add curr prob (for denominator) -- also NOT log prob
            curr_prob += 10 ** curr_dict[word2]
        # now add to dict
        # TO DO need to deal with when it is zero/undefined
        backoff_weights[cluster] = log(1-prev_prob, 10) - log(1-curr_prob, 10)
    
    return backoff_weights


## calculates the discounting factor based on Good-Turing smoothing
# input: ngram count dictionary
# output: discounting factor for that count
# TO DO replace with simple GT!!!!!
def calc_discount(count_dict):
    # dictionary for keeping the discounts
    disc_dict = {}
    # discount depends on count only
    for count in count_dict:
        # if count + 1 not in the dict, will get a discount factor of 0
        if count + 1 in count_dict:
            # standard GT estimation (log of discount)
            numerator = log(count + 1, 10) + log(count_dict[count+1], 10)
            denominator = log(count, 10) + log(count_dict[count], 10)
            disc_dict[count] = numerator - denominator
        # otherwise, just do count/(count+1)
        else:
            disc_dict[count] = log(count, 10) - log(count + 1, 10)
    return disc_dict


## calculates log maximum likelihood probability
# input: count of bigrams, count of unigrams (prior)
# output: log max likelihood
def calc_max_likely(num_count, denom_count):
    numerator = log(num_count, 10)
    denominator = log(denom_count, 10)
    
    return numerator - denominator


## reads in factor file and stores in a dictionary
# input: name of the factor file 
#        format: word factor\n (or factor1 factor\n for factor-factor matchings)
#        only one word per line
# output: dictionary with format {word:factor} or {factor1:factor2}
# NOTE this is not currently used in code (derive factors from training)
def get_factor_dict(filename):
    # dictionary to store factors
    factor_dict = {}
    
    # open the factor file
    with open(filename, 'r') as factor_file:
        # read through line by line
        for line in factor_file:
            # split word from factor (separated by space)
            split_line = line.strip().split(' ')
            # line should consist only of word and factor!
            if len(split_line) != 2:
                print("Your factor file is not in the correct format!")
                print("Line contains " + len(split_line) + " parts")
                print("File: " + filename)
                sys.exit(1)
            # word should not appear twice in factor file!
            if split_line[0] in factor_dict:
                print("Your factor file is not in the correct format!")
                print("word " + split_line[0] + " appears more than once")
                print("File: " + filename)
                sys.exit(2)
            # add the word and its factor to the dictionary
            factor_dict[split_line[0]] = split_line[1]
    
    return factor_dict


## breaks a word-cluster trio into parts (word or cluster)
# input: word in format W-word|S-short|L-large, desired part label
# output: relevant part of the word (word, small cluster, or large cluster)
# TO DO later add check / return error if we can't find part label
def get_part(word, part_label):
    # find the beginning of the cluster (preceded by part label and '-')
    part_start = word.find(part_label + '-')
    # find the end of the cluster ('|' indicates next cluster)
    part_end = word[part_start:].find('|')
    # if we actually reached the end of the word (no part after this one)
    if part_end == -1:
        # just go to the end of the word
        part_end = len(word[part_start:])
    # include everything except the label itself and the dash
    return word[part_start + 2:part_start + part_end]


## calculates bigram probabilities from a bigram count dictionary
# input: bigram count dict, unigram count dict (for normalization), discount dict
# output: probability dict {word1:{word2:probability}}
# TO DO combine with probs_uni
def probs_bi(bigram_counts, normalizer, disc_dict):
    # dictionary to store bigram probs {word1:{word2:prob}}
    prob_dict = {}
    # want a probability for each bigram in the dict
    for word1 in bigram_counts:
        # set up a new dictionary in the prob dict for {word2:prob}
        prob_dict[word1] = {}
        # then loop through the word2s and get the bigram probs of word1 word2
        for word2 in bigram_counts[word1]:
            # get log disc (depends on the count of the bigram)
            disc = disc_dict[bigram_counts[word1][word2]]
            # get log max likelihood
            ml = calc_max_likely(bigram_counts[word1][word2], normalizer[word1])
            # prob = d*max likely; add to dict
            prob_dict[word1][word2] = disc + ml
    
    # once we've gone through all bigrams, we are done
    return prob_dict


## calculats unigram probabilities from a unigram count dictionary
# input: unigram count dict, vocab size (for normalization), discount dict
# output: probability dict ({word:prob})
def probs_uni(unigram_counts, vocab_size, disc_dict):
    # dictionary to store unigram counts {word:probability}
    prob_dict = {}
    # want a probability for each word in the dict
    for word in unigram_counts:
        # get log disc
        disc = disc_dict[unigram_counts[word]]
        # get log max likelihood
        ml = calc_max_likely(unigram_counts[word], vocab_size)
        # prob = d*max likely; add to disc
        prob_dict[word] = disc + ml
    
    # once we've gone through al unigrams, we are done
    return prob_dict
