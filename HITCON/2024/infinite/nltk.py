import nltk

wn = nltk.corpus.wordnet

syn = wn.synsets('Omega Point')
print(syn)
