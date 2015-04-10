# Multidimensional Backoff

Author: Anna Currey  
Created: March 2015  
Hosted on: https://github.com/annacurrey/multidimensional-backoff/tree/master/text-process


### Overview
---
This project is an implementation of multidimensional backoff for factored language models.

##### Current status
There is a script for creating a multidimensional back language model for bigrams with three clusters. There are also text processing scripts for preparing training and test data for use in multidimensional backoff models.

##### To dos
1. Querying program for the language model
2. Script for creating language model for trigrams with two clusters (inc. word)
3. Implement better discounting in language model
4. Generalize scripts to n-grams with m clusters
5. Check calculations of probabilities and back


### Text processing
---
The `text-process` directory contains scripts for converting training and test data into the correct format.

##### add-factors.py
Adds two sets of factors to a data set for use in a factored language model.

Usage: `./add-factors.py [infile] [factor1] [label1] [factor2] [label2] > outfile`

Input: 
	* data file to which factors should be added
		* one sentence per line
		* words separated by spaces
		* no additional tags
	* file containing the first set of factors
		* one word per line
		* format: "[word] [factor label]"
	* label for the first set of factors (one letter)
	* file containing the second set of factors (same format as other factors file) (map from first set to second set)
	* label for the second set of factors
	* desired outfile name

Output: file identical to infile, except that factors have been added
	words are of the format: W-word|A-factor1|B-factor2 (A and B factor labels)

Notes: In the SRILM implementation of factored language models, factors need to be separated with “:”. Here, I separate them with “|”.

##### word2cluster.py
Replaces words in a file with their corresponding clusters.

Usage: `./word2cluster.py infile clusterfile > outfile`

Input file format:
	* one sentence per line
	* words separated by spaces

Cluster file format: 
	* one word per line
	* line format: word cluster
	* no other information in file
	* one cluster per word

Output file format: 
	* identical to input file, but words replaced with their clusters
	* words without clusters are not replaced
	* note we don't replace unclustered words with -1 here because we don't want them to cluster with other words if we run the word clustering program again

Notes: For use in creating the larger set of clusters, if you want to force the smaller clusters to be proper subsets of the larger clusters.



### Creating the language model
---
The program `create-lm_2g3c.py` creates a language model for multidimensional backoff for bigrams with three clusters (including the word itself).

Usage: `./create-lm_2g3c.py training_file > output_file`

Training file format: 
	* one sentence per line
	* words separated by space
	* words in the format W-word|S-small_cluster|L-large_cluster
	* assume small clusters are subsets of large clusters (i.e. given small know large)
	* also assume word-cluster mapping is 1-1

Output file format: 
	* similar to ARPA file format
	* cannot use traditional ARPA format because the backoffs are in a different dimension 



### About multidimensional backoff
---
Multidimensional backoff is used adapt factored language models for use with word vectors. For more information on multidimensional backoff, see the paper [here](https://github.com/annacurrey/multidimensional-backoff/blob/master/Currey_multidimensional-backoff.pdf).