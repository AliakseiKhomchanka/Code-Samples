# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 19:36:55 2018

Filling plaintext with additional letters to make all letters' probabilities
equal to make cryptoanalysis more difficult. Added blocks will be immidiately
recognized by a real person looking at the text, but for a program that gathers
text's statistics, all probabilities will be approximately equal. 

Added "pseudowords" are also shuffled around a bit, so that you wouldn't get 
a long sequence of repeating symbols.

Extended text, in theory, can be quickly cleaned with nlp tools by throwing out
words not present in the vocabulary, leaving only relevant data.

This thing is inefficient as it significantly inscreases the size of data, 
but I guess you can mess with people. I mean, even if someone deciphers the 
word "irbiwbfwbfehbf", who in their right mind would believe it's actualy 
a correct result?

@author: Aliaksei Khomchanka
"""
import random
import re

def equalizePlain(plaintext = 'Okay, so this is a plaintext. There are many texts like this, but this one is mine. And I bet i can make it so difficult that you will never figure it out. Or maybe you will, who knows'):
    plaintext = plaintext.lower().replace(" ","  ").replace(".","").replace(",","")
    items = set(plaintext)
    items.remove(" ")

    freqs = dict((i,0) for i in items)
    for i in plaintext:
        if i in items:
            freqs[i] = freqs[i] + 1  
    maxFreq = max(freqs.values())

    print("Plaintext (all lowercase adn punctuation removed): \n", plaintext, "\n")
    print("Frequency distribution in the plaintext: \n", freqs, "\n")
    print("Maximal frequency in the plaintext: \n", maxFreq, "\n")

    chars = list(plaintext)
    fillingIndices = []

    i = 0
    while i < len(chars):
        if chars[i] == ' ':
            i = i + 1
            fillingIndices.append(i)
        i = i + 1

    fillings = {}
    fillingsNumber = len(fillingIndices)

    for i in range(0,fillingsNumber):
        fillings[i] = {}
        fillings[i]["text"] = ""
        fillings[i]["coordinate"] = fillingIndices[i]

    for currentChar in items:
        i = 0
        while freqs[currentChar] < maxFreq:
            fillings[i]["text"] = fillings[i]["text"] + currentChar
            freqs[currentChar] = freqs[currentChar] + 1
            i = (i + 1) % fillingsNumber

    for i in range(0,fillingsNumber):
        toBeShuffled = list(fillings[i]["text"])
        random.shuffle(toBeShuffled)
        splitsNumber = len(toBeShuffled)//4
        if splitsNumber > 0:
            splitStep = len(toBeShuffled)//splitsNumber
        else:
            splitStep = 1;
        for j in range(0,splitsNumber):
            drift = random.randint(-2,2)
            toBeShuffled = toBeShuffled[:j*splitStep + drift] + [" "] + toBeShuffled[j*splitStep + drift:]
        fillings[i]["text"] = toBeShuffled

    for i in reversed(range(0,fillingsNumber)):
        chars = chars[:fillings[i]["coordinate"]] + [" "] + fillings[i]["text"] + [" "] + chars[fillings[i]["coordinate"]:]

    extendedPlaintext = " ".join("".join(chars).replace("  "," ").split())
    print("Extended plaintext: \n", extendedPlaintext, "\n")

    freqs = dict((i,0) for i in items)
    for i in extendedPlaintext:
        if i in items:
            freqs[i] = freqs[i] + 1      
    maxFreq = max(freqs.values())

    print("Frequency distribution in the extended plaintext: \n", freqs, "\n")
    print("Extended plaintext is",len(extendedPlaintext)/len(plaintext),"times larger than the plaintext.")
               
    blackBlock = u'\u25A0'
    profile = re.sub('[0-9a-zA-Z]', blackBlock, extendedPlaintext)
    print("\nExtended text profile: \n", profile)
    
    wordsList = set(extendedPlaintext.split(" "))
    
    lengths = [len(word) for word in wordsList]
    lengths = set(lengths)
    
    print(wordsList)
    
    lengthFreqs = dict((i,0) for i in lengths)
    for i in wordsList:
        howLong = len(i)
        if howLong in lengths:
            lengthFreqs[howLong] = lengthFreqs[howLong] + 1  
     
    print(lengthFreqs)
    
    print("\nWord lengths frequency distribution in extended plaintext:\n")
    for word in lengthFreqs:
        print('{0:2d}'.format(word), ": ", blackBlock*lengthFreqs[word], "\n")
    
equalizePlain()
