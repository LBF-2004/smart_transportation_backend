import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

def tokenization (data) -> list: # token words from sentence
    token = []
    for sentences in data:
        token.append(nltk.word_tokenize(sentences))
    return token
#tokens = tokenization(["A Duie Pyle – $490.32 – 1 Business Day", "ESTES – $460.34 – 1 Business Day"])

def tag (tokens):  # tagging words (NN, NP...)
    tag_list = []
    for token in tokens:
        tag_list.append(nltk.pos_tag(token))
    return tag_list
# tags = tag(tokens)
# print(tags)


grammar = """PRICE:{<[$]><CD>}
             DETAIL:{<DT>?<VBG>?(<NN>|<NNS>|<NNP>|<JJ>|<ORGANIZATION>|<PERSON>|<[.]>|<GPE>|<CD>|<RB>|<IN>)+<VBD>?<[:]>?<MD>?<VBP>?<VB>?<VBZ>?(<[(]>(<JJ>|<CD>)<NN><NNS><[)]>)?<[:]>?<PRICE>}
             DETAIL:{<DT>?<VBG>?(<NN>|<NNS>|<NNP>|<JJ>|<ORGANIZATION>|<PERSON>|<[.]>|<GPE>|<CD>|<RB>|<IN>)+<VBD>?<[:]>?<VBP>?<VB>?<VBZ>?(<[(]>(<JJ>|<CD>)<NNP>(<NN>|<NNS>)<[)]>)?<PRICE>}
             DETAIL:{<PRICE><DT>?<VBG>?(<NN>|<NNS>|<NNP>|<JJ>|<ORGANIZATION>|<PERSON>|<[.]>|<GPE>|<CD>|<RB>|<IN>)+<VBP>?<VB>?}"""

def chunk(sentence):  # make word with tags into a tree
    first_pass = nltk.ne_chunk(sentence)
    chunker = nltk.RegexpParser(grammar)
    return chunker.parse(first_pass)
def extractTree(tree, label): # get part of tree with particular label = collection of tags that follow grammar implemented
    entity_name = []
    if hasattr(tree, "label") and tree.label:
        if tree.label() == label:
            entity_name.append(tree)
        else:
            for child in tree:
                entity_name.extend(extractTree(child, label))
    return entity_name

def tokenizetagChunk(sentences): # big function to wrap up above
    tokenizer = tokenization(sentences)
    tagization = tag (tokenizer)
    chunkization= []
    for chunks in tagization:
        chunkization.append(chunk(chunks))
    return chunkization

def extractPrice(sentences):
    price_list = []
    chunkization = tokenizetagChunk(sentences)
    for i in chunkization:
        trees = extractTree(i, "PRICE")
        trees_detail = extractTree(i, "DETAIL")
        if trees:
            for j in trees:
                price = ' '.join([w for w, t in j.leaves()])
            for z in trees_detail:
                price_detail = ' '.join([w for w, t in z.leaves()])
            price_list.append({"DETAIL": price_detail, "PRICE": price})




            # join function convert list -> string, seperate by space
            # [] after: break up word (w) and tag (t), only extract word
            # j.leaves function return tuple [(w1, tag1), (w2, tag2)...]
    return price_list
print(extractPrice(["Hello, the deliv rate is $300.50. Thanks"]))

