import random

# generate a random bit order
# you'll need to save this mapping permanently, perhaps just hardcode it
# map how ever many bits you need to represent your integer space
mapping = range(30)
mapping.reverse()
#random.shuffle(mapping)

# alphabet for changing from base 10
chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

# shuffle the bits
def encode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << mapping[i]
        if n & b1:
            result |= b2
    return result

# unshuffle the bits
def decode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << mapping[i]
        if n & b2:
            result |= b1
    return result

# change the base
def enbase(x):
    n = len(chars)
    if x < n:
        return chars[x]
    return enbase(x/n) + chars[x%n]

# go back to base 10
def debase(x):
    n = len(chars)
    result = 0
    for i, c in enumerate(reversed(x)):
        result += chars.index(c) * (n**i)
    return result

def get_id_from_short_url(short_url):
    id_number = decode(debase(short_url))
    return id_number

def get_short_url_from_id(id_number):
    short_url = enbase(encode(id_number))
    return short_url