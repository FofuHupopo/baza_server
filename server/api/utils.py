import difflib


def sort_by_similarity(original, strings):
    ratios = [(string, difflib.SequenceMatcher(None, original, string).ratio()) for string in strings]
    sorted_strings = sorted(ratios, key=lambda x: x[1], reverse=True)
    sorted_strings = [
        string
        for string, coincidence in sorted_strings
        if coincidence > 0
    ]
    return sorted_strings
