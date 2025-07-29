# tests/test_core.py

import pytest
from grapes_tokenizer.core import GrapesTokenizer

@ pytest.mark.parametrize("text, expected", [
    # Letters with positional weighting: value * (position index + 1)
    ("a", 1 * 1),                              # 'a'=1 at pos0
    ("abc", 1*1 + 2*2 + 3*3),                 # 1 + 4 + 9 = 14
    ("xyz", 24*1 + 25*2 + 26*3),              # 24 + 50 + 78 = 152
    ("Hello", 8*1 + 5*2 + 12*3 + 12*4 + 15*5), # weighted sum
])
def test_simple_letters(text, expected):
    tok = GrapesTokenizer()
    assert tok.encode(text) == expected


def test_digits_mapping():
    tok = GrapesTokenizer()
    # '0'->0*1=0, '5'->5*2=10, '9'->9*3=27 => 37
    assert tok.encode("059") == 0 + 10 + 27


def test_specials_mapping():
    tok = GrapesTokenizer()
    # space=32*1=32, '!'=33*2=66, '@'=64*3=192 => 290
    assert tok.encode(" !@") == 32 + 66 + 192


def test_mixed_characters():
    tok = GrapesTokenizer()
    # "a1!b": a=1*1=1, '1'=1*2=2, '!'=33*3=99, b=2*4=8 => 110
    assert tok.encode("a1!b") == 1 + 2 + 99 + 8


def test_empty_string():
    tok = GrapesTokenizer()
    assert tok.encode("") == 0


def test_long_text_performance():
    # a mix of printable ASCII characters repeated
    long_text = "".join(chr((i % 94) + 33) for i in range(1000))
    tok = GrapesTokenizer()
    result = tok.encode(long_text)
    assert isinstance(result, int)
    assert result > 0
