#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

Sébastien Le Maguer <slemaguer@coli.uni-saarland.de>

DESCRIPTION

LICENSE
This script is in the public domain, free from copyrights or restrictions.
Created: 10 February 2017
"""

import sys
import os
import traceback
import argparse
import time
import logging


from roots import *
from roots3p import *

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
UNKNOWN_VALUE = "x"

###############################################################################
# Functions
###############################################################################
def print_carac(name, ipa_alphabet, nsa_alphabet, left="", right=""):
    map_cat2phon = ipa_alphabet.list_phonemes_by_categories()
    nss_map = nsa_alphabet.get_alphabet_map()

    phone_set = set()
    for k in map_cat2phon.keys():
        list_val = map_cat2phon[k]
        if not list_val:
            continue

        q = "QS \"%s-%s\" {" % (name, k)
        for val in range(len(list_val)-1):
            phone_set.add(list_val[val])
            q += "%s%s%s, " % (left, list_val[val], right)
        q += "%s%s%s}" % (left, list_val[-1], right)
        print(q)

    # Phone set part
    phone_set = list(phone_set)
    q = "QS \"%s-%s\" {" % (name, "phones")
    for val in range(len(phone_set)-1):
        q += "%s%s%s, " % (left, phone_set[val], right)
    q += "%s%s%s}" % (left, phone_set[-1], right)
    print(q)

    # Each phone part now
    for ph in phone_set:
        q = "QS \"%s-%s\" {%s%s%s}" % (name, ph, left, ph, right)
        print(q)

    # NSS
    list_nss = nss_map.keys()
    q = "QS \"%s-%s\" {" % (name, "nss")
    for val in range(len(list_nss)-1):
        nss = list_nss[val]
        nss = nss.replace("#", "dash")
        nss = nss.replace("%", "percent")
        q += "%s%s%s, " % (left, nss, right)
    nss = list_nss[-1]
    nss.replace("#", "dash")
    nss.replace("%", "percent")
    q += "%s%s%s}" % (left, list_nss[-1], right)
    print(q)

    for nss in list_nss:
        nss = nss.replace("#", "dash")
        nss = nss.replace("%", "percent")
        q = "QS \"%s-%s\" {%s%s%s}" % (name, nss, left, nss, right)
        print(q)

    # Unknown value
    q = "QS \"%s-%s\" {%s%s%s}" % (name, UNKNOWN_VALUE, left, UNKNOWN_VALUE, right)
    print(q)

def print_seq(name, start, end, left="", right=""):
    # Inf values
    for last in range(start, end+1):
        q = "QS \"%s<=%d\" {" % (name, last)
        for cur in range(start, last):
            q += "%s%d%s, " % (left, cur, right)
        q += "%s%d%s}" % (left, last, right)
        print(q)

    # Equal values
    for last in range(start, end+1):
        q = "QS \"%s==%d\" {%s%d%s}" % (name, last, left, last, right)
        print(q)


    # Unknown value
    q = "QS \"%s==%s\" {%s%s%s}" % (name, UNKNOWN_VALUE, left, UNKNOWN_VALUE, right)
    print(q)

def print_boolean(name, left="", right=""):
    print("QS \"%s==0\" {%s0%s}" % (name, left, right))
    print("QS \"%s==1\" {%s1%s}" % (name, left, right))

    # Unknown value
    q = "QS \"%s==%s\" {%s%s%s}" % (name, UNKNOWN_VALUE, left, UNKNOWN_VALUE, right)
    print(q)

###############################################################################
# Main function
###############################################################################
def main():
    """Main entry function
    """
    global args

    ipa_alphabet = phonology_ipa_IrisaAlphabet.get_instance()
    nsa_alphabet = phonology_nsa_IrisaNsAlphabet.get_instance()

    # Phone part
    print_carac("LL", ipa_alphabet, nsa_alphabet, "", "^*")
    print_carac("L", ipa_alphabet, nsa_alphabet, "*^", "-*")
    print_carac("C", ipa_alphabet, nsa_alphabet, "*-", "+*")
    print_carac("N", ipa_alphabet, nsa_alphabet, "*+", "=*")
    print_carac("NN", ipa_alphabet, nsa_alphabet, "*=", "@*")
    print("\n\n")

    # Utterance part
    print_seq("NB_SYLS_IN_UTT", 1, 50, "*/J:", "+*")
    print_seq("NB_WORDS_IN_UTT", 1, 30, "*+", "-*")
    print_seq("NB_PHRASES_IN_UTT", 1, 10, "*-", "/Z:*")

###############################################################################
#  Envelopping
###############################################################################
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="")

        # Add options
        parser.add_argument("-v", "--verbosity", action="count", default=0,
                            help="increase output verbosity")

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

# roots2question.py ends here
