#http://stackoverflow.com/a/1052896/2026118
import random

mapping = range(30)
mapping.reverse()
random.shuffle(mapping)

ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'


def encode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << mapping[i]
        if n & b1:
            result |= b2
    return result


def decode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << mapping[i]
        if n & b2:
            result |= b1
    return result


def enbase(x):
    n = len(ALPHABET)
    if x < n:
        return ALPHABET[x]
    return enbase(x / n) + ALPHABET[x % n]


def debase(x):
    n = len(ALPHABET)
    result = 0
    for i, c in enumerate(reversed(x)):
        result += ALPHABET.index(c) * (n ** i)
    return result


def get_id_from_short_url(short_url):
    id_number = decode(debase(short_url))
    return id_number


def get_short_url_from_id(id_number):
    short_url = enbase(encode(id_number))
    return short_url
