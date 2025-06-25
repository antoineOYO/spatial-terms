###################################################################
# defining basic objects :
#  - sampled sentences
#  - found patterns matching any pattern from our catalog 
###################################################################

import json
import conllu

class sample(dict):
    def __init__(
            self,
            conllu_str:str,
            id:str = None,
    ):
        """
        Sentence sampled from a corpus.
        May contain multiple sentences itself.

        :param conllu_str: The CoNLL-U formatted string of the sentence, with eventually metadata 'text' and 'sent_id'
        :param id: Unique identifier for the sentence to use if 'sent_id' metadata is not present in the conllu_str.
        """
        
        self['conllu_str'] = conllu_str
        self.conllu = conllu.parse(conllu_str)

        metadata_id = self.conllu[0].metadata.get('sent_id')
        if metadata_id and not id:
            self['id'] = self.conllu[0].metadata.get('sent_id', id)
        elif id:
            self['id'] = id
        else:
            raise ValueError("Either 'sent_id' metadata must be present in the conllu_str or an 'id' must be provided.")

        # Extract tokens and store them in a list
        tokens = [token["form"] for sent in self.conllu for token in sent if isinstance(token["id"], int)]
        self['tokens'] = tokens
        self['text'] = self.conllu[0].metadata.get('text', ' '.join(tokens))
        

    def __str__(self):
        return json.dumps(self, indent=2, ensure_ascii=False)


class pattern(sample):
    def __init__(
            self,
            conllu_str:str,
            footprint: list[int],
            id:str = None,
            sub_sent_id: int = 0,
    ):
        """
        found pattern in a `sample` instance

        :param footprint: list of indexes of the tokens which form the pattern, i.e. positions of the matched nodes
        :param sub_sent_id: the id of the sentence in which the pattern was found (our sample can contain multiple sentences)
        """
        super().__init__(conllu_str, id, )
        self['sub_sent_id'] = sub_sent_id
        self['footprint'] = footprint
        
        self['minimal_span'] = self._get_span(sub_sent_id, window=0)

    def _get_span(self, sent_id, window: int = 0) -> str:
        """
        builds the minimal span of the text covered by the pattern footprint.

        :param sent_id: the id of the sentence in which the pattern was found
        :param neighbors: windows of tokens to include around the pattern footprint
        """
        if not self['footprint']:   
            return ""

        # Get the start and end indices from the pattern footprint
        # Note: CoNLL-U uses 1-based indexing, so we need to adjust accordingly
        start_index = min(self['footprint'])-1
        start_index = max(0, start_index - window)
        end_index = max(self['footprint'])-1
        end_index = min(len(self['tokens']) - 1, end_index + window)

        # Extract the tokens from the conllu data
        tokens = [token['form'] for token in self.conllu[sent_id] if isinstance(token["id"], int)]
        
        # Join the tokens to form the minimal span text
        min_span_text = ' '.join(tokens[start_index:end_index + 1])
        
        return min_span_text


    def __str__(self):
        return json.dumps(self, indent=2, ensure_ascii=False)

    
if __name__ == "__main__":

    # Example CoNLL-U (twisted)
    data = """
    # sent_id = test0
    # text = !The quick brown fox jumps over the lazy dog. the lazy dog
    1   The     the    DET    DT   Definite=Def|PronType=Art   4   det     _   _
    2   quick   quick  ADJ    JJ   Degree=Pos                  4   amod    _   _
    3   brown   brown  ADJ    JJ   Degree=Pos                  4   amod    _   _
    4   fox     fox    NOUN   NN   Number=Sing                 5   nsubj   _   _
    5   jumps   jump   VERB   VBZ  Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin   0   root    _   _
    6   over    over   ADP    IN   _                           9   case    _   _
    7   the     the    DET    DT   Definite=Def|PronType=Art   9   det     _   _
    8   lazy    lazy   ADJ    JJ   Degree=Pos                  9   amod    _   _
    9   dog     dog    NOUN   NN   Number=Sing                 5   nmod    _   SpaceAfter=No
    10  .       .      PUNCT  .    _                           5   punct   _   _

    1   the     the    DET    DT   Definite=Def|PronType=Art   9   det     _   _
    2   lazy    lazy   ADJ    JJ   Degree=Pos                  9   amod    _   _
    3   dog     dog    NOUN   NN   Number=Sing                 5   nmod    _   SpaceAfter=No
    """

    # Example usage
    sample_instance = sample(
        conllu_str=data,
        id='overwrite-metadata',

    )
    print(sample_instance)
    print('---'*30)

    # Suppose we search for patterns like [AGENT + VERB + PREP + GROUND]
    # The `footprint` of the `pattern` corresponds to the indexes of the tokens forming the pattern
    # based on the conllu string numerotation (1-based indexing).
    # Here the footprint would be [4, 5, 6, 9]
    pattern_instance = pattern(
        conllu_str=sample_instance['conllu_str'],
        footprint=[4, 5, 6, 9],
        # no id provided : metadata 'sent_id' will be used
        )
    print(pattern_instance)

    data2 = """
    # sent_id = blc-fr-complex-ln-cop
    # text = Il était au bord du chemin
    1	Il	il	_	PRON	_	5	nsubj	_	_
    2	était	était	_	AUX	_	5	cop	_	_
    3-4	au	_	_	_	_	_	_	_	_
    3	à	à	_	ADP	_	5	case	_	_
    4	le	le	_	DET	_	5	det	_	_
    5	bord	bord	_	NOUN	_	0	root	_	_
    6-7	du	_	_	_	_	_	_	_	_
    6	de	de	_	ADP	_	8	case	_	_
    7	le	le	_	DET	_	8	det	_	_
    8	chemin	chemin	_	NOUN	_	5	nmod	_	SpaceAfter=No
    """
    sample_instance2 = sample(
        conllu_str=data2,
        id='blc-fr-complex-ln-cop',
    )
    pattern_instance2 = pattern(
        conllu_str=sample_instance2['conllu_str'],
        footprint=[1, 8]
    )
    print(pattern_instance2)

