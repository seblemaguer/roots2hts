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

import sys
import os
import traceback
import argparse
import time
import logging
import roots
import shutil
import queue
from threading import Thread

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

###############################################################################
# Functions
###############################################################################
class WavExtraction(Thread):
    def __init__(self, queue, sequence_labels = None):
        """
        """
        Thread.__init__(self)
        self.queue = queue

        if sequence_labels is not None:
            self.sequence_labels = sequence_labels
        else:
            self.sequence_labels = dict()
            self.sequence_labels["signal"] = "Signal"

    def run(self):
        """
        """
        while True:
            utt_infos = self.queue.get()
            if utt_infos is None:
                break


            # Get informations
            id = utt_infos[0]
            utt = utt_infos[1].get_utterance(id)
            out_dir = utt_infos[2]

            # Generate path
            signal_sequence = utt.get_sequence(self.sequence_labels["signal"]).as_segment_sequence()
            item = signal_sequence.get_item(0).as_signal_segment()
            in_wav_path = os.path.join(item.get_base_dir_name(), item.get_file_name())
            out_wav_path = os.path.join(out_dir, "%s.wav" % id)

            # Copy now
            shutil.copyfile(in_wav_path, out_wav_path)

            # Over !
            print("%d.wav has been extracted" % id)
            self.queue.task_done()

###############################################################################
# Main function
###############################################################################
def main():
    """Main entry function
    """
    global args

    corpus = roots.Corpus(args.corpus)

    # Convert duration to labels
    q = queue.Queue()
    threads = []
    for base in range(args.nb_proc):
        t = WavExtraction(q)
        t.start()
        threads.append(t)

    for i in range(0, corpus.count_utterances()):
        utt = [i, corpus, args.output_dir]
        q.put(utt)


    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(len(threads)):
        q.put(None)

    for t in threads:
        t.join()

###############################################################################
#  Envelopping
###############################################################################
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="")

        # Add options
        parser.add_argument("-v", "--verbosity", action="count", default=0,
                            help="increase output verbosity")
        parser.add_argument("-p", "--nb_proc", default=1, type=int,
                            help="nb process in parallel")
        parser.add_argument("corpus")
        parser.add_argument("output_dir")

        # Add arguments
        # Example : parser.add_argument("echo", help="description")
        # TODO

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
