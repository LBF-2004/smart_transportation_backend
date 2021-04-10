import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words') 

sentence = """At eight o'clock on Thursday morning
... Arthur didn't feel very good."""
tokens = nltk.word_tokenize(sentence)
tokens

tagged = nltk.pos_tag(tokens)
tagged[0:6]



entities = nltk.chunk.ne_chunk(tagged)
print (entities)


sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),
("dog", "NN"), ("barked", "VBD"), ("at", "IN"),  ("the", "DT"), ("cat", "NN")]

grammar = """SS: {<DT>?<JJ>*<CD>}
AB:{<RB>*<JJ>}"""
cp = nltk.RegexpParser(grammar)
result = cp.parse(tagged)
print(result)

result.draw()

def tokenization (data) -> list:
    token = []
    for sentences in data:
        token.append(nltk.word_tokenize(sentences))
    return token
tokens = tokenization(["A Duie Pyle – $490.32 – 1 Business Day", "ESTES – $460.34 – 1 Business Day"])

def tag (tokens):
    tag_list = []
    for token in tokens:
        tag_list.append(nltk.pos_tag(token))
    return tag_list
tags = tag(tokens)
print(tags)


