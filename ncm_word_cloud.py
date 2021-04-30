#!/Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/venv python
# ------------------------------------------------------------------------------
# Script name:  speech_graph.py
#
# Description:
#               Script to visualise sentence using OpenIE5 and Stanford CoreNLP
#
# Author:       Caroline Nettekoven, 2020
#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# source /Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/venv/bin/activate
# Usage: python ./speech_graph.py 3
#        tat=3; python -u ./speech_graph.py ${tat} > figures/SpeechGraph_log_${tat}_`date +%F` # (pipe output to text file)
# TODO: Plot graphs coloured by confidence / extraction type
# TODO: Look at the few transcripts that threw errors and debug them
# TODO: Look at stanza graph edges and see if they are correct
# ------------------------------------------------------------------------------


import os
import os.path as op
from pathlib import Path
import stanza
import pandas as pd
from stanza.server import CoreNLPClient
import sys
sys.path.append(
    '/Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/')
from pyopenie import OpenIE5
import matplotlib.pyplot as plt
from copy import deepcopy
from itertools import chain
import numpy as np
from nlp_helper_functions import expand_contractions, remove_interjections, replace_problematic_symbols, remove_irrelevant_text, process_sent, get_transcript_properties, remove_duplicates, remove_bad_transcripts
from visualise_paragraph_functions import create_edges_ollie, create_edges_stanza, get_word_types, get_adj_edges, get_prep_edges, get_obl_edges, add_obl_edges, get_node_synonyms, split_node_synonyms, split_nodes, merge_corefs, clean_nodes, clean_parallel_edges, add_adj_edges, add_prep_edges, get_unconnected_nodes
# from filelists import tat_pilot_files, hbn_movie_files, genpub_files, all_tat_files, dct_story_files
import time
import datetime
# ------------------------------------------------------------------------------
# Time execution of script
start_time = time.time()
# ------------------------------------------------------------------------------
# Get sentence
# selected_file = 1
# selected_file = 2916


# Import selected transcript
input_file = '/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/NCM_talk_abstracts.txt'
# filename = input_file.name
with open(input_file, 'r') as fh:
    orig_text = fh.read()


with open('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/list_of_brain_areas.txt', 'r') as fh:
    brain_areas = fh.read()

brain_areas = brain_areas.split('\n')

for area in brain_areas:
    if area.lower() in text:
        print(area)
# ------------------------------------------------------------------------------
# ------- Clean text -------
# Need to replace problematic symbols before ANYTHING ELSE, because other tools cannot work with problematic symbols
# text = replace_problematic_symbols(orig_text)  # replace ’ with '
# text = expand_contractions(text)  # expand it's to it is
# text = remove_interjections(text)  # remove Ums and Mmms
# text = remove_irrelevant_text(text)
# text = text.strip()  # remove trailing and leading whitespace

text = orig_text.strip()  # remove trailing and leading whitespace
text = text[:50000]
# ------------------------------------------------------------------------------
# ------- Print transcript name -------
transcript = filename.strip('.txt')
print("\n+++ Transcript +++ \n\n %s" % (transcript))


# ------------------------------------------------------------------------------
# ------- Print cleaned text -------
print("\n+++ Paragraph: +++ \n\n %s \n\n+++++++++++++++++++" % (text))

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------- Run Stanford CoreNLP (Stanza) -------
# Annotate and extract with Stanford CoreNLP

with CoreNLPClient(properties={
    'annotators': 'tokenize,ssplit,pos,lemma,parse,depparse,coref,openie'
    # 'pos.model': '/Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/OpenIE-standalone/target/streams/$global/assemblyOption/$global/streams/assembly/8a3bd51fe5c1bb09a51f326fa358947f6dc78463_8e7f18d9ae73e8daf5ee4d4e11167e10f8827888_da39a3ee5e6b4b0d3255bfef95601890afd80709/edu/stanford/nlp/models/pos-tagger/english-bidirectional/english-bidirectional-distsim.tagger'
}, be_quiet=True) as client:
    ex_stanza = client.annotate(text)

# ------- Basic Transcript Descriptors -------
n_tokens, n_sententences, _ = get_transcript_properties(text, ex_stanza)

no_noun, poss_pronouns, dts, nouns, nouns_origtext, adjectives = get_word_types(
    ex_stanza)
