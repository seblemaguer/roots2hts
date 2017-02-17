#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <slemaguer@coli.uni-saarland.de>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 29 January 2017
"""
from roots import *

try:
    from roots3p import *
except Exception as ex:
    pass

#####################################################################################################
### Global part
#####################################################################################################
class Feature:
    def __init__(self, utt, sequence_labels):
        self.utt = utt
        self.sequence_labels = sequence_labels

    def compute(self, source_index, prm=None):
        raise NotImplementedError("this method should be overriden")

class FeatureFactory:
    def __init__(self, utt, sequence_labels):
        self.utt = utt
        self.sequence_labels = sequence_labels

    def compute(self, feature, source_index, prm=None):
        return globals()[feature](self.utt, self.sequence_labels).compute(source_index, prm)



#####################################################################################################
### Segment part
#####################################################################################################
UNIT = 10000000 # HTK unit is in 100ns

class StartSegment(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, segment_index, prm=None):
        segments = self.utt.get_sequence(self.sequence_labels["segment"]).as_segment_sequence()
        seg = segments.get_item(segment_index)
        return int(seg.get_segment_start() * UNIT)

class EndSegment(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, segment_index, prm=None):
        segments = self.utt.get_sequence(self.sequence_labels["segment"]).as_segment_sequence()
        seg = segments.get_item(segment_index)
        return int(seg.get_segment_end() * UNIT)



#####################################################################################################
### Phone part
#####################################################################################################
class PhoneIndex(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, segment_index, prm=None):
        """
        """
        phones = self.utt.get_sequence(self.sequence_labels["phone"]).as_phoneme_sequence()
        rel_seg_phones = self.utt.get_relation(self.sequence_labels["segment"], self.sequence_labels["phone"])
        rel_phones_indexes = rel_seg_phones.get_related_elements(segment_index)
        if rel_phones_indexes:
            return rel_phones_indexes[0]
        return None

class PhoneLabel(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phoneme_index, prm=None):
        """
        """
        phones = self.utt.get_sequence(self.sequence_labels["phone"]).as_phoneme_sequence()
        cur_phone = phones.get_item(phoneme_index)
        return cur_phone.to_string()


class NssIndex(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, segment_index, prm=None):
        """
        """
        nss = self.utt.get_sequence(self.sequence_labels["nss"])
        rel_seg_nss = self.utt.get_relation(self.sequence_labels["segment"], self.sequence_labels["nss"])
        rel_nss_indexes = rel_seg_nss.get_related_elements(segment_index)
        if rel_nss_indexes:
            return rel_nss_indexes[0]
        return None

class NssLabel(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, nss_index, prm=None):
        """
        """
        nss = self.utt.get_sequence(self.sequence_labels["nss"])
        label = nss.get_item(nss_index).to_string()
        label = label.replace("#", "dash")
        label = label.replace("%", "percent")
        return label

class PhoneInSyllableFW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phoneme_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"])
        rel_phones_syllables = self.utt.get_relation(self.sequence_labels["phone"], self.sequence_labels["syllable"])
        rel_syllables_phones = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["phone"]) # FIXME: inverse

        idx_syllable = rel_phones_syllables.get_related_elements(phoneme_index)
        if idx_syllable:
            idx_syllable = idx_syllable[0]
            idx_phones = rel_syllables_phones.get_related_elements(idx_syllable)
            fw_idx = (phoneme_index - idx_phones[0]) + 1
            return fw_idx

        return None


class PhoneInSyllableBW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phoneme_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"])
        rel_phones_syllables = self.utt.get_relation(self.sequence_labels["phone"], self.sequence_labels["syllable"])
        rel_syllables_phones = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["phone"]) # FIXME: inverse

        idx_syllable = rel_phones_syllables.get_related_elements(phoneme_index)
        if idx_syllable:
            idx_syllable = idx_syllable[0]
            idx_phones = rel_syllables_phones.get_related_elements(idx_syllable)
            bw_idx = (idx_phones[-1] - phoneme_index) + 1
            return bw_idx

        return None


#####################################################################################################
### Syllable part
#####################################################################################################
class SyllableIndex(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phone_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"])
        rel_seg_syllables = self.utt.get_relation(self.sequence_labels["phone"], self.sequence_labels["syllable"])
        rel_syllables_indexes = rel_seg_syllables.get_related_elements(phone_index)
        if rel_syllables_indexes:
            return rel_syllables_indexes[0]
        return None

class SyllableIsStressed(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"]).as_syllable_sequence()

        syllable = syllables.get_item(syllable_index)
        return syllable.is_stressed()

class SyllableIsProminent(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"]).as_syllable_sequence()

        syllable = syllables.get_item(syllable_index)
        return syllable.is_prominent()


class SyllableSizeInPhones(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"]).as_syllable_sequence()

        syllable = syllables.get_item(syllable_index)
        return len(syllable.to_phoneme_indices())



class SyllableInWordFW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        words = self.utt.get_sequence(self.sequence_labels["word"])
        rel_syllables_words = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["word"])
        rel_words_syllables = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["syllable"]) # FIXME: inverse

        idx_word = rel_syllables_words.get_related_elements(syllable_index)
        if idx_word:
            idx_word = idx_word[0]
            idx_syllables = rel_words_syllables.get_related_elements(idx_word)
            fw_idx = (syllable_index - idx_syllables[0]) + 1
            return fw_idx

        return None

class SyllableInWordBW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        words = self.utt.get_sequence(self.sequence_labels["word"])
        rel_syllables_words = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["word"])
        rel_words_syllables = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["syllable"]) # FIXME: inverse

        idx_word = rel_syllables_words.get_related_elements(syllable_index)
        if idx_word:
            idx_word = idx_word[0]
            idx_syllables = rel_words_syllables.get_related_elements(idx_word)
            bw_idx = (idx_syllables[-1] - syllable_index) + 1
            return bw_idx

        return None



class SyllableInPhraseFW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        rel_syllables_phrases = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["phrase"])
        rel_phrases_syllables = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["syllable"]) # FIXME: inverse

        idx_phrase = rel_syllables_phrases.get_related_elements(syllable_index)
        if idx_phrase:
            idx_phrase = idx_phrase[0]
            idx_syllables = rel_phrases_syllables.get_related_elements(idx_phrase)
            fw_idx = (syllable_index - idx_syllables[0]) + 1
            return fw_idx

        return None

class SyllableInPhraseBW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        rel_syllables_phrases = self.utt.get_relation(self.sequence_labels["syllable"], self.sequence_labels["phrase"])
        rel_phrases_syllables = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["syllable"]) # FIXME: inverse

        idx_phrase = rel_syllables_phrases.get_related_elements(syllable_index)
        if idx_phrase:
            idx_phrase = idx_phrase[0]
            idx_syllables = rel_phrases_syllables.get_related_elements(idx_phrase)
            bw_idx = (idx_syllables[-1] - syllable_index) + 1
            return bw_idx

        return None


class SyllableVowel(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, syllable_index, prm=None):
        """
        """
        syllables = self.utt.get_sequence(self.sequence_labels["syllable"]).as_syllable_sequence()

        syllable = syllables.get_item(syllable_index)
        nuc = syllable.get_nucleus()
        if nuc:
            return nuc[0].to_string()
        return None



#####################################################################################################
### Word part
#####################################################################################################
class WordIndex(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phone_index, prm=None):
        """
        """
        words = self.utt.get_sequence(self.sequence_labels["word"])
        rel_seg_words = self.utt.get_relation(self.sequence_labels["phone"], self.sequence_labels["word"])
        rel_words_indexes = rel_seg_words.get_related_elements(phone_index)
        if rel_words_indexes:
            return rel_words_indexes[0]
        return None


class WordSizeInSyllable(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, word_index, prm=None):
        """
        """

        rel_words_syllables = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["syllable"])
        syllables = rel_words_syllables.get_related_elements(word_index)
        return len(syllables)


class WordInPhraseFW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, word_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        rel_words_phrases = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["phrase"])
        rel_phrases_words = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["word"]) # FIXME: inverse

        idx_phrase = rel_words_phrases.get_related_elements(word_index)
        if idx_phrase:
            idx_phrase = idx_phrase[0]
            idx_words = rel_phrases_words.get_related_elements(idx_phrase)
            fw_idx = (word_index - idx_words[0]) + 1
            return fw_idx

        return None

class WordInPhraseBW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, word_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        rel_words_phrases = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["phrase"])
        rel_phrases_words = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["word"]) # FIXME: inverse

        idx_phrase = rel_words_phrases.get_related_elements(word_index)
        if idx_phrase:
            idx_phrase = idx_phrase[0]
            idx_words = rel_phrases_words.get_related_elements(idx_phrase)
            bw_idx = (idx_words[-1] - word_index) + 1
            return bw_idx

        return None


class WordPOS(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, word_index, prm=None):
        """
        """

        rel_words_pos = self.utt.get_relation(self.sequence_labels["word"], self.sequence_labels["pos"])
        pos= rel_words_pos.get_related_items(word_index)
        if pos:
            return pos[0].to_string()
        return None


#####################################################################################################
### Phrase part
#####################################################################################################
class PhraseIndex(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phone_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        rel_seg_phrases = self.utt.get_relation(self.sequence_labels["phone"], self.sequence_labels["phrase"])
        rel_phrases_indexes = rel_seg_phrases.get_related_elements(phone_index)
        if rel_phrases_indexes:
            return rel_phrases_indexes[0]
        return None


class PhraseSizeInSyllable(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phrase_index, prm=None):
        """
        """

        rel_phrases_syllables = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["syllable"])
        syllables = rel_phrases_syllables.get_related_elements(phrase_index)
        return len(syllables)

class PhraseSizeInWord(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phrase_index, prm=None):
        """
        """

        rel_phrases_words = self.utt.get_relation(self.sequence_labels["phrase"], self.sequence_labels["word"])
        words = rel_phrases_words.get_related_elements(phrase_index)
        return len(words)


class PhraseInUtteranceFW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phrase_index, prm=None):
        """
        """
        return phrase_index + 1

class PhraseInUtteranceBW(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, phrase_index, prm=None):
        """
        """
        phrases = self.utt.get_sequence(self.sequence_labels["phrase"])
        return (phrases.count() - phrase_index)


#####################################################################################################
### Utterance part
#####################################################################################################
class UtteranceSizeInSyllable(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, index, prm=None):
        """
        """
        return self.utt.get_sequence(self.sequence_labels["syllable"]).count()

class UtteranceSizeInWord(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, index, prm=None):
        """
        """
        return self.utt.get_sequence(self.sequence_labels["word"]).count()


class UtteranceSizeInPhrase(Feature):
    def __init__(self, utt, sequence_labels):
        Feature.__init__(self, utt, sequence_labels)

    def compute(self, index, prm=None):
        """
        """
        return self.utt.get_sequence(self.sequence_labels["phrase"]).count()
