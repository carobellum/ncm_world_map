#!/Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/venv python
# ------------------------------------------------------------------------------
# Script name:  ncm_world_cloud.py
#
# Description:
#               Script to create a list of words used in the ncm abstracts as a first step to create a word cloud
#
# Author:       Caroline Nettekoven, 2020
#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# source /Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/venv/bin/activate
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
from process_text import get_transcript_properties, list_of_words, remove_irrelevant_words
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


# ------------------------------------------------------------------------------
# ------- Clean text -------
# Need to replace problematic symbols before ANYTHING ELSE, because other tools cannot work with problematic symbols
# text = replace_problematic_symbols(orig_text)  # replace ’ with '
# text = expand_contractions(text)  # expand it's to it is
# text = remove_interjections(text)  # remove Ums and Mmms
# text = remove_irrelevant_text(text)
# text = text.strip()  # remove trailing and leading whitespace

list_of_paragraphs = orig_text.split('\n')
list_of_dfs = []
text_cleaned = ''
for paragraph in list_of_paragraphs:
    #
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------
    # ------- Run Stanford CoreNLP (Stanza) -------
    # Annotate and extract with Stanford CoreNLP
    #
    with CoreNLPClient(properties={
        'annotators': 'tokenize,ssplit,pos,lemma,parse,depparse,coref,openie'
        # 'pos.model': '/Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/OpenIE-standalone/target/streams/$global/assemblyOption/$global/streams/assembly/8a3bd51fe5c1bb09a51f326fa358947f6dc78463_8e7f18d9ae73e8daf5ee4d4e11167e10f8827888_da39a3ee5e6b4b0d3255bfef95601890afd80709/edu/stanford/nlp/models/pos-tagger/english-bidirectional/english-bidirectional-distsim.tagger'
    }, be_quiet=True) as client:
        ex_stanza = client.annotate(paragraph)
    #
    # ------- Clean text of irrelevant words -------
    cleaned_paragraph, cleaned_paragraph_word_list = remove_irrelevant_words(
        ex_stanza)
    #
    text_cleaned = text_cleaned + cleaned_paragraph
    # ------- Create dataframe -------
    df_paragraph = pd.DataFrame(
        {'word': cleaned_paragraph_word_list})
    #
    list_of_dfs.append(df_paragraph)

df = pd.concat(list_of_dfs)
df.to_csv(input_file.strip('.txt') + '_df.csv')
df.value_counts().head(20)

text_file = open(input_file.strip('.txt') + '_cleaned.txt', "w")
n = text_file.write(text_cleaned)
text_file.close()

# list_of_words = nouns_origtext + adjectives
# df = pd.DataFrame(
#     {'type': ['noun'] * len(nouns_origtext) + ['adjective'] * len(adjectives), 'word': list_of_words})


# ------- Count brain areas mentioned -------
# with open('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/list_of_brain_areas.txt', 'r') as fh:
#     brain_areas = fh.read()

# brain_areas = brain_areas.split('\n')

# for area in brain_areas:
#     if area.lower() in text:
#         print(area)

# # ------- Basic Transcript Descriptors -------
# n_tokens, n_sententences, _ = get_transcript_properties(
#     paragraph, ex_stanza)
#
# no_noun, poss_pronouns, dts, nouns, nouns_origtext, adjectives = list_of_words(
#     ex_stanza)
#
