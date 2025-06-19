###################################################################
# defining our Semgrex patterns
# they will be incorporated into the catalog ALL_PATTERNS
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

BLUE, RED, GREEN, RESET = "\033[94m", "\033[91m", "\033[92m", "\033[0m"

class semgrexPattern:
    _used_names = set()

    def __init__(
            self,
            name: str,
            desc: str,
            basic: str,
            enhanced: str = None,
    ):
        """
        Syntactic pattern written in Semgrex syntax.
        documentation: 
        https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html
        
        :param name: Unique name for the pattern
        :param desc: example sentence or description of the pattern
        :param basic: Semgrex pattern in basicDependencies
        :param enhanced: Semgrex pattern in enhancedDependencies (optional, if not provided, basic is used)
        """
        if name in semgrexPattern._used_names:
            raise ValueError(f"Pattern name '{name}' already used")
        semgrexPattern._used_names.add(name)
        self.name = name
        self.desc = desc
        self.basic = basic
        self.enhanced = enhanced if enhanced else basic
    
    def __str__(self):
        msg = f"Pattern: {self.name}"
        msg += f"\nDescription: {self.desc}"
        msg += f"{BLUE}\nBasic:\n{self.basic}{RESET}"
        msg += f"{GREEN}\nEnhanced:\n{self.enhanced}{RESET}"
        return msg
    
#%% simple patterns
  
pattern1 = "{}=ground"
pattern1 += " >nsubj {}=figure"
pattern1 += " >cop {}=verb"
pattern1 += " >case {pos:IN}=st0"
pattern1 += " : {}=figure .. {}=verb"
pattern1 += " : {}=verb .. {}=st0"
pattern1 += " : {}=st0 .. {}=ground"

MY_PATTERN_1 = semgrexPattern(
    name = 'blc-en-simple-ground',
    desc = 'The chalet is among the trees and animals. \nHer favorite spot is off the beaten track.',
    basic = pattern1,
)

pattern7 = "{}=st0"
pattern7 += " >nsubj {}=figure"
pattern7 += " >cop {}=verb"
pattern7 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern7 += " >case {pos:IN}=st1"
pattern7 += " )"
pattern7 += " : {}=figure .. {}=verb"
pattern7 += " : {}=verb .. {}=st0"
pattern7 += " : {}=st0 . {}=st1"
pattern7 += " : {}=st1 .. {}=ground"

MY_PATTERN_7 = semgrexPattern(
    name = 'blc-en-simple-iln-obl',
    desc = 'The needle is right of centre.',
    basic = pattern7,
)

pattern8 = "{pos:VBN}=st0"
pattern8 += " >/nsubj:pass/ {}=figure"
pattern8 += " >/aux:pass/ {}=verb"
pattern8 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern8 += " >case {pos:IN}=st1"
pattern8 += " )"
pattern8 += " : {}=figure .. {}=verb"
pattern8 += " : {}=verb .. {}=st0"
pattern8 += " : {}=st0 . {}=st1"
pattern8 += " : {}=st1 .. {}=ground"

MY_PATTERN_8 = semgrexPattern(
    name = 'blc-en-simple-iln-aux',
    desc = 'She was left of the building.',
    basic = pattern8,
)

pattern9 = " {}=figure"
pattern9 += " >/^dep.*|^acl.*/ ( {tag:/VB.*/}=verb"
pattern9 += " >advmod ( {pos:RB}=st0"
pattern9 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern9 += " >case {pos:IN}"
pattern9 += " )))"
pattern9 += " : {}=figure .. {}=verb"
pattern9 += " : {}=verb .. {}=st0"
pattern9 += " : {}=st0 .. {}=ground"
MY_PATTERN_9 = semgrexPattern(
    name = 'blc-en-simple-figure',
    desc = 'It is north of London. \nThey were North of the city.',
    basic = pattern9,
)
#%% complex patterns
pattern2 = "{}=ground"
pattern2 += " >nsubj {}=figure"
pattern2 += " >cop {}=verb"
pattern2 += " >case ( {pos:IN}=st1"
pattern2 += " >fixed {pos:NN}=st0"
pattern2 += " >fixed {pos:IN}=st2"
pattern2 += " )"
pattern2 += " : {}=figure .. {}=verb"
pattern2 += " : {}=verb .. {}=st1"
pattern2 += " : {}=st1 . {}=st0"
pattern2 += " : {}=st0 . {}=st2"
pattern2 += " : {}=st2 .. {}=ground"
MY_PATTERN_2 = semgrexPattern(
    name = 'blc-en-complex-ground-fixed',
    desc = 'All of a sudden they were in front of us.',
    basic = pattern2,
)


pattern4 = "{pos:NN}=st0"
pattern4 += " >nsubj {}=figure"
pattern4 += " >cop {}=verb"
pattern4 += " >case {pos:IN}=st1"
pattern4 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern4 += " >case {pos:IN}=st2"
pattern4 += " )"
pattern4 += " : {}=figure .. {}=verb"
pattern4 += " : {}=verb .. {}=st1"
pattern4 += " : {}=st1 . {}=st0"
pattern4 += " : {}=st0 . {}=st2"
pattern4 += " : {}=st2 .. {}=ground"
MY_PATTERN_4 = semgrexPattern(
    name = 'blc-en-complex-iln-nmod',
    desc = 'We are in back of the yards, as instructed.',
    basic = pattern4,
)

pattern5 = "{pos:NN}=st0"
pattern5 += " >nsubj {}=figure"
pattern5 += " >cop {}=verb"
pattern5 += " >case {pos:IN}=st1"
pattern5 += " >det {}=st2"
pattern5 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern5 += " >case {pos:IN}=st3"
pattern5 += " )"
pattern5 += " : {}=figure .. {}=verb"
pattern5 += " : {}=verb .. {}=st1"
pattern5 += " : {}=st1 . {}=st2"
pattern5 += " : {}=st2 . {}=st0"
pattern5 += " : {}=st0 . {}=st3"
pattern5 += " : {}=st3 .. {}=ground"
MY_PATTERN_5 = semgrexPattern(
    name = 'blc-en-complex-iln-det',
    desc = 'The paytable will be to the right of the screen.',
    basic = pattern5,
)

pattern3 = "{}=verb"
pattern3 += " >nsubj {}=figure"
pattern3 += " >advmod ( {}=st0"
pattern3 += " >advmod {}=st1"
pattern3 += " >/^nmod.*|^obl.*/ ( {}=ground"
pattern3 += " >case {pos:IN}=st2"
pattern3 += " ))"
pattern3 += " : {}=figure .. {}=verb"
pattern3 += " : {}=verb .. {}=st1"
pattern3 += " : {}=st1 . {}=st0"
pattern3 += " : {}=st0 . {}=st2"
pattern3 += " : {}=st2 .. {}=ground"
MY_PATTERN_3 = semgrexPattern(
    name = 'blc-en-complex-verb',
    desc = 'Location was far off from downtown.',
    basic = pattern3
)
#%% other patterns found
pattern9bis = "{}=verb"
pattern9bis += " >nsubj {}=figure"
pattern9bis += " >advmod ( {}=st0"
pattern9bis += " >/^obl.*/ ( {}=ground"
pattern9bis += " >case {}=st1"
pattern9bis += " ))"
pattern9bis += " : {}=figure .. {}=verb"
pattern9bis += " : {}=verb .. {}=st0"
pattern9bis += " : {}=st0 . {}=st1"
pattern9bis += " : {}=st1 .. {}=ground"
MY_PATTERN_9bis = semgrexPattern(
    name = 'blc-en-simple-verb',
    desc = 'It is north of London.',
    basic = pattern9bis,
)

pattern3bis = "{}=ground"
pattern3bis += " >nsubj {}=figure"
pattern3bis += " >cop {}=verb"
pattern3bis += " >case {}=st2"
pattern3bis += " >advmod ( {}=st0"
pattern3bis += " >advmod {}=st1"
pattern3bis += " )"
pattern3bis += " : {}=figure .. {}=verb"
pattern3bis += " : {}=verb .. {}=st1"
pattern3bis += " : {}=st1 . {}=st0"
pattern3bis += " : {}=st0 . {}=st2"
pattern3bis += " : {}=st2 .. {}=ground"
MY_PATTERN_3bis = semgrexPattern(
    name = 'blc-en-complex-ground-advmod',
    desc = 'Location was far off from downtown.',
    basic = pattern3bis,
)

#%% existantial patterns
pattern10 = "{}=verb"
pattern10 += " >expl {}=exist"
pattern10 += " >nsubj ( {}=figure"
pattern10 += " >/^nmod.*/ ( {}=ground"
pattern10 += " >case {}=st0"
pattern10 += " ))"
pattern10 += " : {}=exist .. {}=verb"
pattern10 += " : {}=verb .. {}=figure"
pattern10 += " : {}=figure .. {}=st0"
pattern10 += " : {}=st0 .. {}=ground"
MY_PATTERN_10 = semgrexPattern(
    name = 'existantial-en-simple-verb',
    desc = 'There is a prize in the wrapper.',
    basic = pattern10,
    enhanced = pattern10
)

pattern11 = "{}=verb"
pattern11 += " >expl {}=exist"
pattern11 += " >nsubj ( {}=figure"
pattern11 += " >/^nmod.*/ ( {}=st0"
pattern11 += " >case {}=st1"
pattern11 += " >/^nmod.*/ {}=ground"
pattern11 += " ))"
pattern11 += " : {}=exist .. {}=verb"
pattern11 += " : {}=verb .. {}=figure"
pattern11 += " : {}=figure .. {}=st1"
pattern11 += " : {}=st1 .. {}=st0"
pattern11 += " : {}=st0 .. {}=ground"
MY_PATTERN_11 = semgrexPattern(
    name = 'existantial-en-complex-verb',
    desc = 'There is a prize on top of the wrapper.',
    basic = pattern11,
    enhanced = pattern11
)


#%% collecting all patterns
ALL_PATTERNS = [v for v in globals().values() if isinstance(v, semgrexPattern)]
PATTERNS_INDEX = {index: p.name for index,p in enumerate(ALL_PATTERNS)}

if __name__ == "__main__":
    import json
    for p in ALL_PATTERNS:
        print(p)
        print()

    
    print(json.dumps(PATTERNS_INDEX, indent=2, ensure_ascii=False))