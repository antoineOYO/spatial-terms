######################################################################
# Performs the lexico-syntactic search
# lexico : searches for spatial terms in the pattern
# syntactic : searches for the syntactic structure of the pattern
#
# Terminology :
# - BLC : Base Locative Construction
# - Existantial : a BLC with an "existential" phrase, i.e. "there is", "there were"
# - LN : Localization Noun such as "east" in the complex preposition "in the east of"
# - we use "figure" and "ground"
# - st0 : 'central' spatial term :
#   for simple prepositions, it is the preposition itself, e.g. "on", "in", "above"
#   for complex prepositions, the Localization Noun ("top" in "on top of")
# - st1, st2 : for the case of complex prepositions, other spatial terms surrounding the Localization Noun st0
#   "in the center of" --> "in":st1, "the":st2, "center":st0", "of": st3
# - verb : the copula or the verb governing the BLC
######################################################################

# our tools 
from myCorpusObjects import * # classes `sample` and `pattern`
from mySemgrexPatterns import * # importing our semgrex patterns through ALL_PATTERNS catalog

from stanza.server import semgrex
from stanza.utils.conll import CoNLL
from google.protobuf.json_format import MessageToDict
import pandas as pd

# setting up the CoreNLP resources
import os
resources = os.path.expanduser("~/resources/")
corenlp_dir = os.path.join(resources, "stanford-corenlp-4.5.8/")
os.environ["CORENLP_HOME"] = corenlp_dir

#%% basic "be" english lemmatizer
# A simple lemmatizer for the verb "be" in English
# TODO : use in case no lemmatisation is provided in the CoNLL-U string
be_forms = [
    'am', 'are', 'is', 'was', 'were', 'been', 'being', 'be',
    "'m", "'re", "'s",  # contractions
    "ain't", "aren't", "isn't", "wasn't", "weren't",
    "ain’t", "aren’t", "isn’t", "wasn’t", "weren’t"  # negated forms
]

simple_lemmatizer_en = {form: 'be' for form in be_forms}

#%% auxiliary functions

def import_spatial_lexeme(file='spatial_terms.csv') -> tuple[dict, dict]:
    """reads both spatial prepositions and localization nouns"""
    spatial_terms = pd.read_csv(file).dropna(how='all')
    LNs = {} # Localization Nouns
    PREPs = {} # Prepositions (simple)
    for _, row in spatial_terms.iterrows():
        if pd.notna(row['LN']):
            LNs[row['LN']] = row
        else:
            PREPs[row['alphabetical_marker'].split(' ')[0]] = row
    return LNs, PREPs


LNs, PREPs = import_spatial_lexeme()

def has_spatial_lexeme(pattern:pattern, LNs:dict, PREPs:dict):
    """checks if a pattern entails a term with potential spatial meaning"""
    term = pattern.get('st0', '_')
    term.lower() # to ensure case insensitivity
    if isinstance(term, str) and (term in PREPs.keys() or term in LNs.keys()):
        return True
    else :
        return False

def to_pattern(
        my_sample:sample, 
        semgrexMatches:dict,
) -> list[pattern]:
    """
    converts a CoreNLP Semgrex match into a pattern instance.
    """
    POTENTIAL_BLC = []

    # peeling the semgrex matches dict
    for sent_id,sent in enumerate(semgrexMatches.get("result", [])):
        for mdict in sent.get("result", []) :
            for match in mdict.get('match', []):
                
                # if nodes were named in the semgrex pattern :
                if match.get("node") :
                    unorderedNodes = {n.get("name"): n.get("matchIndex") for n in match.get("node", [])}
                    orderedNodes = sorted(unorderedNodes.items(), key=lambda x: x[1])
                    footprint = [n[1] for n in orderedNodes]

                    # instanciating a pattern object
                    current_pBLC = pattern(
                        id=my_sample.get("id"),
                        conllu_str=my_sample.get("conllu_str"),
                        footprint=footprint,
                        sub_sent_id=sent_id,
                    )

                    # adding extra info specific of BLC
                    nodes = dict(orderedNodes)
                    figure_id, st0_id, ground_id = nodes.get("figure"), nodes.get("st0"), nodes.get("ground")
                    pattern_id = match.get("semgrexIndex", "_")
                    pattern_name = PATTERNS_INDEX.get(pattern_id, "unknown_pattern")
                    current_pBLC.update(
                        {
                            "nodes": nodes,
                            "patternName": pattern_name,
                            "figure": current_pBLC.conllu[sent_id][figure_id-1]["form"],
                            "st0": current_pBLC.conllu[sent_id][st0_id-1]["form"],
                            "ground": current_pBLC.conllu[sent_id][ground_id-1]["form"],
                            "hash": current_pBLC.get('id') + f":subsent-{sent_id}" + f":{pattern_name}:{figure_id}-{st0_id}-{ground_id}",
                        }
                    )
                
                    POTENTIAL_BLC.append(current_pBLC)

    return POTENTIAL_BLC

#%% main filtering functions    
def filter(
    my_sample:sample,
    patterns:list[semgrexPattern] = ALL_PATTERNS,
    enhanced:bool = False,   
) -> list[pattern]:
    """
    performs the lexico-syntactic filtering of the conllu string
    returns a list of pBLC instances

    :param my_sample: a sample instance containing the conllu_str to be filtered
    :param patterns: a list of semgrexPattern instances to be used for filtering (default: ALL_PATTERNS from mySemgrexPatterns.py)
    :param enhanced: whether to search for enhancedDependencies or not (default: False)
    """
    
    # CONLL-U to stanza.doc
    doc = CoNLL.conll2doc(input_str=my_sample.get("conllu_str"))

    # building patterns string catalog
    PATTERNS = [p.enhanced if enhanced else p.basic for p in patterns]

    # search for all the patterns
    try:
        results = semgrex.process_doc(doc, *PATTERNS, enhanced=enhanced)
    except Exception as e:
        raise RuntimeError(f"Semgrex failed on sample ID={my_sample.get('id')} with error: {e}")
    

    # convert the results to a dict
    semgrex_dict = MessageToDict(results)

    # convert to a 'match' format
    patterns = to_pattern(my_sample, semgrexMatches=semgrex_dict)

    # discard patterns with no lexical items potentially spatial (ie. in spatial_lexicon.keys())
    raw_patterns = [
        p for p in patterns if has_spatial_lexeme(p, LNs, PREPs)
    ]

    return raw_patterns
    
def resolve(
        raw_patterns:list[pattern], 
        verbose:bool = False,
        lang= 'en',
) -> list[pattern]:
    """
    Resolves conflicts between `pattern`.
    Returns a refined set `pattern`
    
    **Language specific**
    
    :param raw_patterns: a list of pattern instances to be resolved
    :param lang: language specific mode (TODO)
    """
    if verbose:
        print('--- All matches')
        for match in raw_patterns:
            print('\033[38;5;208;1m', match.get("minimal_span"), '\033[0m')

    refined_set = []

    # TODO : search for the head of relative clause
    # relative clause modifier
    # (acl:relcl = a subtype of acl, clausal modifier of noun).

    # Ensuring that the verb is 'be' in the matches 
    for match in raw_patterns:
        verb_id = match.get("nodes", {}).get("verb", "_")
        verb_token = match.conllu[match['sub_sent_id']][verb_id - 1]['form']
        if simple_lemmatizer_en.get(verb_token, "_") == 'be':
            refined_set.append(match)       
    if verbose:
        print('--- With "be" as verb')
        for match in refined_set:
            print('\033[34;1m', match.get("minimal_span"), '\033[0m') 
    
    # removing simple preposition patterns embedded into complex prepositions 
    refined_set = [
        match for i, match in enumerate(refined_set)
        if not any(
            i != j
            and match.get("sent_id") == other_match.get("sent_id")
            and match.get("nodes", {}).get("ground") == other_match.get("nodes", {}).get("st0")
            and match.get("nodes", {}).get("figure") == other_match.get("nodes", {}).get("figure")
            and "complex" in other_match.get("patternName")
            for j, other_match in enumerate(refined_set)
        )
    ]

    # removing patterns with simple prepositions embedded into complex prepositions and sharing figure and ground
    refined_set = [
        match for i, match in enumerate(refined_set)
        if not any(
            i != j
            and match.get("sent_id") == other_match.get("sent_id")
            and match.get("nodes", {}).get("ground") == other_match.get("nodes", {}).get("ground")
            and match.get("nodes", {}).get("figure") == other_match.get("nodes", {}).get("figure")
            and "complex" in other_match.get("patternName")
            and "simple" in match.get("patternName", "")
            for j, other_match in enumerate(refined_set)
        )
    ]
    if verbose:
        print('--- With no concurrent')
        for match in refined_set:
            print('\033[32;1m', match.get("minimal_span"), '\033[0m')

    return refined_set


#%% main
if __name__ == "__main__":

    with open("examples.conllu", "r", encoding="utf-8") as f:
        parsed_corpus = [b for b in f.read().split("\n\n\n") if b.strip()]
        
    for sentences in parsed_corpus:

        # instanciating a sample object.
        # The CONLL-U string must contain metadata 'text' and 'sent_id'
        # and is parsed by the `sample` class    
        my_sample = sample(
            conllu_str=sentences
        )
        print('-'*30)
        print('\033[1m', my_sample['text'], '\033[0m')
        print('-'*30)
        print(my_sample['conllu_str'])
        

        # seach based on the whole catalog, then resolution of overlapping patterns
        # (i.e. patterns sharing for example the same figure and ground)
        potentialBLC = resolve(filter(my_sample), verbose=True)
        for p in potentialBLC:
            print('Figure :', p.get("figure"))
            print('st0 :', p.get("st0"))
            print('Ground :', p.get("ground"))
            print('Pattern name :', p.get("patternName"))
            print(p)
        print('\n\n\n')