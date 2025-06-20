# spatial-terms

We provide here a lexico-syntactic filter, based on Semgrex [1].
- `spatial_terms.ods` is the lexicon of spatial terms
- `mySemgrexPatterns.py` is the catalog of syntactic patterns
- `syntacticFilter.py` operates the joint lexical and syntactic search of patterns
- `myCorpusObjects.py` defines the main classes `sample` and `pattern` used in the code, explained next

> **Note**: `syntacticFilter.py` executes two main steps: `filter()` for pattern matching and `resolve()` for post-processing. The `resolve()` function is language-specific and handles disambiguation of overlapping matches.


### Inputs

Each input includes:  
1) a CoNLL-U formatted sentence  
2) a mandatory unique sentence identifier (used for downstream processing)

Inputs are structured into `sample` objects, minimally as:

```json
{   
    "conllu_str" : "1   The     the    DET    DT   Definite=Def|PronType=Art   4   det     _   _",
    "id" : "test0",
    "tokens" : ["The"],
    "text" : "The"
}
```
- `conllu_str` raw CoNLL-U string, optionally with `# text` and `# sent_id` metadata
- `id` : sentence identifier
- `tokens` : list of tokens extracted from the CoNLL-U
- `text` : sentence text (from metadata if present, else joined from tokens)

> **NOTE :** the code handles single CoNLL-U inputs with multiple sub-sentences (as it is often the case for bitexts).

### Output

Each match is returned as a `pattern` object, for example:

```json
{
    "conllu_str" : "1   The     the    DET    DT   Definite=Def|PronType=Art   4   det     _   _",
    "id" : "test0",
    "tokens" : ["The"],
    "text" : "The",
    "sub_sent_id": 0,
    "footprint": [1],
    "minimal_span": "The"
}
```
- `sub_sent_id`: sub-sentences index for disambiguation
- `footprint`: indices of matched nodes
- `minimal_span`: surface span ranging over the `footprint`

### Special Outputs for Basic Locative Constructions and Existential Statements

For BLCs and other complex spatial expressions, additional fields are included:
- `patternName` : the name of the pattern matched
- `figure` : the Figure text
- `st0` : "main" term of the preposition (see terminology in the code)
- `ground` : the Ground text
- `hash` a unique identifier for each found pattern (compiles `id`, `sub_sent_id`, `patternName` and `footprint`)
- `nodes` : a dictionnary {role:index} where the role is `figure`, `ground` etc

### Example : an Existential Statement
Input :
```txt
# sent_id = existantial-sample
# text = There is a prize on top of the wrapper.
1	There	there	_	EX	_	2	expl	_	_
2	is	be	_	VBZ	_	0	root	_	_
3	a	a	_	DT	_	4	det	_	_
4	prize	prize	_	NN	_	2	nsubj	_	_
5	on	on	_	IN	_	6	case	_	_
6	top	top	_	NN	_	4	nmod	_	_
7	of	of	_	IN	_	9	case	_	_
8	the	the	_	DT	_	9	det	_	_
9	wrapper	wrapper	_	NN	_	6	nmod	_	SpaceAfter=No
10	.	.	_	.	_	2	punct	_	SpaceAfter=No
```

Output :
```json
{
  "conllu_str": "...",
  "id": "existantial-sample",
  "tokens": [
    "There",
    "is",
    "a",
    "prize",
    "on",
    "top",
    "of",
    "the",
    "wrapper",
    "."
  ],
  "text": "There is a prize on top of the wrapper.",
  "sub_sent_id": 0,
  "footprint": [
    1,
    2,
    4,
    5,
    6,
    9
  ],
  "minimal_span": "There is a prize on top of the wrapper",
  "nodes": {
    "exist": 1,
    "verb": 2,
    "figure": 4,
    "st1": 5,
    "st0": 6,
    "ground": 9
  },
  "patternName": "existantial-en-complex-verb",
  "figure": "prize",
  "st0": "top",
  "ground": "wrapper",
  "hash": "existantial-sample:subsent-0:existantial-en-complex-verb:4-6-9"
}
```

# Sources
[1] John Bauer, Chloé Kiddon, Eric Yeh, Alex Shan, and Christopher D. Manning. 2023. Semgrex and Ssurgeon, Searching and Manipulating Dependency Graphs Proceedings of the 21st International Workshop on Treebanks and Linguistic Theories (TLT, GURT/SyntaxFest 2023)