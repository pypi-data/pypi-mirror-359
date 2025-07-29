# grapes_tokenizer/core.py

class GrapesTokenizer:
    """
    Sum-based tokenizer with:
      - Letters a–z → 1–26
      - Digits 0–9 → their integer value (0–9)
      - All other characters → ASCII code via ord()
    Always uses positional weighting.
    """

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive
        self.positional = True

    def _char_to_value(self, ch: str) -> int:
        if not self.case_sensitive:
            ch = ch.lower()
        if ch.isalpha():
            return ord(ch) - ord('a') + 1
        if ch.isdigit():
            return int(ch)
        return ord(ch)

    def _binary_add(self, b1: str, b2: str) -> str:
        return bin(int(b1, 2) + int(b2, 2))[2:]

    def encode(self, text: str) -> int:
        """
        Encode a string to its positional sum-based token (decimal).
        """
        total_bin = '0'
        for idx, ch in enumerate(text):
            val = self._char_to_value(ch)
            # apply positional weighting
            val *= (idx + 1)
            b = bin(val)[2:]
            total_bin = self._binary_add(total_bin, b)
        return int(total_bin, 2)
