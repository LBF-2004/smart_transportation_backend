import parseprice
import os
sentence = ["The line haul of this piece would be $50.00"]


token = parseprice.tokenization(sentence)
tags = parseprice.tag(token)
chunks = []
for tag in tags:
    chunks.append(parseprice.chunk(tag))
tree = []
for chunk in chunks:
    tree.extend(parseprice.extractTree(chunk, "PRICE"))
print (tree)
print(parseprice.extractPrice(sentence))
for i in range (1,38):
    file = open("Test/Test" + str (i), "r") # r reads files
    sentences = file.read().split("/n")
    newsentences = [x for x in sentences if x.strip()]




