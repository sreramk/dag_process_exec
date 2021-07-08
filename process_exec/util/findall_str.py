def findall(pattern, string_to_search_in: str):
    """
    Yields all the positions of
    the pattern p in the string s.
    """
    i = string_to_search_in.find(pattern)
    while i != -1:
        yield i
        i = string_to_search_in.find(pattern, i + 1)
