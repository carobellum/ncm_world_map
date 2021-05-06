#!/Users/CN/Documents/Projects/Cambridge/language_analysis/venv python
# ------------------------------------------------------------------------------
# Script name:  visualise_paragraph_functions.py
#
# Description:
#               Functions to get basic text descriptors.
#
# Author:       Caroline Nettekoven, 2020
#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# source /Users/CN/Documents/Projects/Cambridge/cambridge_language_analysis/venv/bin/activate
import os
import os.path as op
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

# ------------------------------------------------------------------------------
# ------- Get text properties -------


def get_transcript_properties(text, ex_stanza):
    punctuation_pos_tags = ['SENT', '.', ':',
                            ',', '(', ')', '"', "'", "`", '$', '#']
    #
    # Count number of tokens that are not punctuation
    total_tokens = 0
    total_punctuations = 0
    #
    for sent in ex_stanza.sentence:
        no_tokens_in_sentence = len(sent.token)
        total_tokens += no_tokens_in_sentence
        #
        for token in sent.token:
            # for word in token.words:
            if token.pos in punctuation_pos_tags:
                # print(token.word, token.pos)
                total_punctuations += 1
    #
    n_tokens = total_tokens - total_punctuations
    #
    #
    n_sententences = len(ex_stanza.sentence)
    #
    return n_tokens, n_sententences, total_punctuations

# ------------------------------------------------------------------------------
# ------- Get word types -------
# First extract a list of determiners present in the text that need to be ignored when matching (You don't want to match "the picture" and "the dog" on "the")


def list_of_words(ex_stanza):
    no_noun = []
    poss_pronouns = []
    dts = []
    nouns = []
    nouns_origtext = []
    adjectives = []
    for sentence in ex_stanza.sentence:
        for token in sentence.token:
            # get nouns (proxy for nodes)
            if token.pos == "PRP" or token.pos == "NN" or token.pos == "NNS":
                nouns.append(token.lemma)
                nouns_origtext.append(token.word.lower())
            # Add everything that is not noun to list of words that should not get merged on later
            else:
                # get words that are not proper nouns (includes pronouns)
                if token.pos == "PRP$":
                    # Lemma for poss pronoun 'his' is 'he', but 'he' counts as noun, therefore add orginial text for poss pronoun
                    no_noun.append(token.word.lower())
                    poss_pronouns.append(token.word.lower())
                else:
                    no_noun.append(token.lemma)
                # get determiners
                if token.pos == "DT":
                    dts.append(token.lemma)
                # get adjectives
                elif token.pos == "JJ":
                    adjectives.append(token.lemma)
    print('++++ Obtained word types ++++')
    return no_noun, poss_pronouns, dts, nouns, nouns_origtext, adjectives


def remove_irrelevant_words(ex_stanza):
    irrelevant_pos_tags = ['CC', 'CD', 'DT', 'EX', 'IN', 'IN / that', 'LS', 'MD',
                           'PDT', 'POS', 'PP', 'PPZ', 'SENT', 'SYM', 'TO', 'UH',
                           'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
                           'VH', 'VHD', 'VHG', 'VHN', 'VHP', 'VHZ',
                           'WDT', 'WP', 'WP$', 'WRB',
                           '#', '$', '“', '``', '(', ')', ',', ':']
    # irrelevant_upos_tags = ['SYM', 'PUNCT', 'PRON', 'DET', 'ADP', 'SYM',
    #                         'PART', 'INTJ', 'PRON', 'DET', 'ADV', 'PUNCT']
    cleaned_text_list = [
        token.originalText.lower() for sentence in ex_stanza.sentence for token in sentence.token if token.pos not in irrelevant_pos_tags]
    cleaned_text = ' '.join(cleaned_text_list)
    return cleaned_text, cleaned_text_list
