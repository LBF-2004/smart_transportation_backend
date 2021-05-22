import parseprice
import os
sentence = ["The Delivery fee is $30", "LTL Freight ESTES Next Day Service $485","Partial TL $550 (1-2 Days)", "Dedicated Van $1000", "Let us know if we can assist with this!"]


token = parseprice.tokenization(sentence)
tags = parseprice.tag(token)
chunks = []
for tag in tags:
    chunks.append(parseprice.chunk(tag))
tree = []
for chunk in chunks:
    tree.extend(parseprice.extractTree(chunk, "PRICE"))
print (tree)

for i in range (1,38):
    file = open("Test/Test" + str (i), "r") # r reads files
    sentences = file.read().split("/n")
    newsentences = [x for x in sentences if x.strip()]
    print(parseprice.extractPrice(newsentences))



