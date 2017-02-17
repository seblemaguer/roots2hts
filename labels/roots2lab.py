#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

Sébastien Le Maguer <slemaguer@coli.uni-saarland.de>

DESCRIPTION

LICENSE
This script is in the public domain, free from copyrights or restrictions.
Created: 28 January 2017
"""
# Standard
import sys
import os
import traceback
import argparse
import time
import logging

import roots
from features import *

# Multi process
from multiprocessing import Process, Queue, JoinableQueue

# Configuration part
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


###############################################################################
# Constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

PH_WIN = 2

###############################################################################
# Utils
###############################################################################
class UtteranceToLabel(Process):
    def __init__(self, corpus, out_lab_dir, queue, config):
        """
        """
        Process.__init__(self)
        self.corpus = corpus
        self.queue = queue
        self.out_dir = out_lab_dir

        # Load configuration
        self.sequence_labels = config["SequenceLabels"]
        self.phoneme_alphabet = config["Alphabets"]["Phone"]
        self.nss_alphabet = config["Alphabets"]["NSS"]

    def fill(self, segment_index, nb_segs):
        """
        """
        feature_factory = FeatureFactory(self.utt, self.sequence_labels)
        nb_syllables = self.utt.get_sequence(self.sequence_labels["syllable"]).count()
        nb_words = self.utt.get_sequence(self.sequence_labels["word"]).count()
        nb_phrases = self.utt.get_sequence(self.sequence_labels["phrase"]).count()

        infos = []

        ###############################################################################
        ## Segment
        ###############################################################################
        infos.append(feature_factory.compute("StartSegment", segment_index))
        infos.append(feature_factory.compute("EndSegment", segment_index))

        ###############################################################################
        ## Phones
        ###############################################################################
        for s in reversed(range(1, PH_WIN+1)):
            if (segment_index-s) >= 0:
                phone_index = feature_factory.compute("PhoneIndex", segment_index-s)
                if phone_index is None:
                    nss_index = feature_factory.compute("NssIndex", segment_index-s)
                    label = feature_factory.compute("NssLabel", nss_index, self.nss_alphabet)
                else:
                    label = feature_factory.compute("PhoneLabel", phone_index, self.phoneme_alphabet)
                infos.append(label)
            else:
                infos.append(None)

        cur_phone_index = feature_factory.compute("PhoneIndex", segment_index)
        if cur_phone_index is None:
            nss_index = feature_factory.compute("NssIndex", segment_index)
            label = feature_factory.compute("NssLabel", nss_index, self.nss_alphabet)
        else:
            label = feature_factory.compute("PhoneLabel", cur_phone_index, self.phoneme_alphabet)
        infos.append(label)

        for s in range(1, PH_WIN+1):
            if (segment_index+s) < nb_segs:
                phone_index = feature_factory.compute("PhoneIndex", segment_index+s)
                if phone_index is None:
                    nss_index = feature_factory.compute("NssIndex", segment_index+s)
                    label = feature_factory.compute("NssLabel", nss_index, self.nss_alphabet)
                else:
                    label = feature_factory.compute("PhoneLabel", phone_index, self.phoneme_alphabet)
                infos.append(label)
            else:
                infos.append(None)


        if cur_phone_index is not None:
            infos.append(feature_factory.compute("PhoneInSyllableFW", cur_phone_index))
            infos.append(feature_factory.compute("PhoneInSyllableBW", cur_phone_index))
        else:
            infos += [None, None]

        ###############################################################################
        ## Syllable
        ###############################################################################
        if cur_phone_index is not None:
            syllable_index = feature_factory.compute("SyllableIndex", cur_phone_index)
            if syllable_index is None:
                print(feature_factory.compute("PhoneLabel", cur_phone_index, self.phoneme_alphabet))

            if syllable_index > 0:
                infos.append(feature_factory.compute("SyllableIsStressed", syllable_index-1))
                infos.append(feature_factory.compute("SyllableIsProminent", syllable_index-1))
                infos.append(feature_factory.compute("SyllableSizeInPhones", syllable_index-1))
            else:
                infos += [None, None, None]


            infos.append(feature_factory.compute("SyllableIsStressed", syllable_index))
            infos.append(feature_factory.compute("SyllableIsProminent", syllable_index))
            infos.append(feature_factory.compute("SyllableSizeInPhones", syllable_index))
            infos.append(feature_factory.compute("SyllableInWordFW", syllable_index))
            infos.append(feature_factory.compute("SyllableInWordBW", syllable_index))
            infos.append(feature_factory.compute("SyllableInPhraseFW", syllable_index))
            infos.append(feature_factory.compute("SyllableInPhraseBW", syllable_index))
            infos += [None for i in range(0,8)] # FIXME: ignore b8 to b15 for now
            infos.append(feature_factory.compute("SyllableVowel", syllable_index))

            if syllable_index < (nb_syllables - 1):
                infos.append(feature_factory.compute("SyllableIsStressed", syllable_index+1))
                infos.append(feature_factory.compute("SyllableIsProminent", syllable_index+1))
                infos.append(feature_factory.compute("SyllableSizeInPhones", syllable_index+1))
            else:
                infos += [None, None, None]


        ###############################################################################
        ## Word
        ###############################################################################
        if cur_phone_index is not None:
            word_index = feature_factory.compute("WordIndex", cur_phone_index)

            if word_index > 0:
                infos.append(feature_factory.compute("WordPOS", word_index-1))
                infos.append(feature_factory.compute("WordSizeInSyllable", word_index-1))
            else:
                infos += [None, None]


            infos.append(feature_factory.compute("WordPOS", word_index))
            infos.append(feature_factory.compute("WordSizeInSyllable", word_index))
            infos.append(feature_factory.compute("WordInPhraseFW", word_index))
            infos.append(feature_factory.compute("WordInPhraseBW", word_index))
            infos += [None for i in range(0,4)] # FIXME: ignore e5 to e8 for now

            if word_index < (nb_words - 1):
                infos.append(feature_factory.compute("WordPOS", word_index+1))
                infos.append(feature_factory.compute("WordSizeInSyllable", word_index+1))
            else:
                infos += [None, None]


        ###############################################################################
        ## Phrase
        ###############################################################################
        if cur_phone_index is not None:
            phrase_index = feature_factory.compute("PhraseIndex", cur_phone_index)

            if phrase_index > 0:
                infos.append(feature_factory.compute("PhraseSizeInSyllable", phrase_index-1))
                infos.append(feature_factory.compute("PhraseSizeInWord", phrase_index-1))
            else:
                infos += [None, None]


            infos.append(feature_factory.compute("PhraseSizeInSyllable", phrase_index))
            infos.append(feature_factory.compute("PhraseSizeInWord", phrase_index))
            infos.append(feature_factory.compute("PhraseInUtteranceFW", phrase_index))
            infos.append(feature_factory.compute("PhraseInUtteranceBW", phrase_index))
            infos.append(None)

            if phrase_index < (nb_phrases - 1):
                infos.append(feature_factory.compute("PhraseSizeInSyllable", phrase_index+1))
                infos.append(feature_factory.compute("PhraseSizeInWord", phrase_index+1))
            else:
                infos += [None, None]


        ###############################################################################
        ## Utterance
        ###############################################################################
        infos.append(feature_factory.compute("UtteranceSizeInSyllable", segment_index))
        infos.append(feature_factory.compute("UtteranceSizeInWord", segment_index))
        infos.append(feature_factory.compute("UtteranceSizeInPhrase", segment_index))

        return infos

    def format(self, infos):
        infos = ['x' if v is None else v for v in infos]
        if len(infos) < 12:
            pass
        elif len(infos) == 12:
            label = "%s %s %s^%s-%s+%s=%s@%s_%s/A:x_x_x/B:x-x-x@x-x&x-x#x-x$x-x!x-x;x-x|x/C:x+x+x/D:x_x/E:x+x@x+x&x+x#x+x/F:x_x/G:x_x/H:x=x^x=x|x/I:x_x/J:%d+%d-%d/Z:x" % tuple(infos)
        else:
            label = "%s %s %s^%s-%s+%s=%s@%s_%s/A:%s_%s_%s/B:%s-%s-%s@%s-%s&%s-%s#%s-%s$%s-%s!%s-%s;%s-%s|%s/C:%s+%s+%s/D:%s_%s/E:%s+%s@%s+%s&%s+%s#%s+%s/F:%s_%s/G:%s_%s/H:%s=%s^%s=%s|%s/I:%s_%s/J:%d+%d-%d/Z:x" % tuple(infos)

        return label

    def run(self):
        """
        """
        while True:
            utt_infos = self.queue.get()
            if utt_infos is None:
                logging.info("Thread is finished")
                break

            self.id = utt_infos
            self.utt = self.corpus.get_utterance(self.id)

            out_handle = open(os.path.join(self.out_dir, "%d.lab" % self.id), "w")

            try:
                segments = self.utt.get_sequence(self.sequence_labels["segment"]).as_segment_sequence()

                nb_segs = segments.count()
                for i in range(0, nb_segs):
                    infos = self.fill(i, nb_segs)
                    label = self.format(infos)
                    out_handle.write("%s\n" % label)

                print("%d is done" % self.id)
            except Exception as ex:
                print("%d failed with exception %s" % (self.id, ex))
            out_handle.close()
            self.queue.task_done()

###############################################################################
# Main function
###############################################################################


###############################################################################
# Main function
###############################################################################
def main():
    """Main entry function
    """
    global args

    # Load configuration
    config = load(args.configuration, Loader=Loader)
    ignored = []
    if "IgnoredID" in config:
        ignored = config["IgnoredID"]

    # Loading corpus
    corpus = roots.Corpus(args.corpus)

    # Convert duration to labels
    q = JoinableQueue()
    processes = []
    for base in range(args.nb_proc):
        t = UtteranceToLabel(corpus, args.output_dir, q, config)
        t.start()
        processes.append(t)

    # Fill the queue for the workers
    for i in range(0, corpus.count_utterances()):
        if i not in ignored:
            q.put(i)

    # Fill the queue by adding a None to indicate the end
    for i in range(len(processes)):
        q.put(None)

    # Wait the end of the processes
    for t in processes:
        t.join()

###############################################################################
#  Envelopping
###############################################################################
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="")

        # Add options
        parser.add_argument("-c", "--configuration", type=open)
        parser.add_argument("-v", "--verbosity", action="count", default=0,
                            help="increase output verbosity")
        parser.add_argument("-p", "--nb_proc", default=1, type=int,
                            help="nb process in parallel")

        # Add arguments
        parser.add_argument("corpus")
        parser.add_argument("output_dir")

        # Parsing arguments
        args = parser.parse_args()

        # Verbose level => logging level
        log_level = args.verbosity
        if (args.verbosity > len(LEVEL)):
            logging.warning("verbosity level is too high, I'm gonna assume you're taking the highes ")
            log_level = len(LEVEL) - 1
        logging.basicConfig(level=LEVEL[log_level])

        # Debug time
        start_time = time.time()
        logging.info("start time = " + time.asctime())

        # Running main function <=> run application
        main()

        # Debug time
        logging.info("end time = " + time.asctime())
        logging.info('TOTAL TIME IN MINUTES: %02.2f' %
                    ((time.time() - start_time) / 60.0))

        # Exit program
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        pass
    except Exception as e:
        logging.error('ERROR, UNEXPECTED EXCEPTION')
        logging.error(str(e))
        traceback.print_exc(file=sys.stderr)
        sys.exit(-1)

# roots2lab.py ends here
