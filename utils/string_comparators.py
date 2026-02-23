import sys
from difflib import SequenceMatcher
from itertools import combinations
from typing import Tuple

from utils.unified_console import console


def find_similar_strings(strings: set[str], similarity_threshold: float = 0.8) -> set[Tuple[str, str, float]]:
    """
    Find pairs of strings that are at least n% similar to each other.

    Args:
        strings: List of strings to compare
        similarity_threshold: Minimum similarity ratio (0.0 to 1.0), e.g., 0.8 for 80%

    Returns:
        List of tuples (string1, string2, similarity_score) for pairs above threshold
    """
    if not strings:
        console.print()
        sys.exit()

    similar_pairs = []

    # Generate all unique pairs of strings
    for str1, str2 in combinations(strings, 2):

        if None in (str1, str2):
            continue

        # Calculate similarity ratio (0.0 to 1.0)
        similarity = SequenceMatcher(None, str1, str2).ratio()

        if similarity >= similarity_threshold:
            similar_pairs.append((str1, str2, similarity))

    # Sort by similarity score (highest first)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    return set(similar_pairs)
