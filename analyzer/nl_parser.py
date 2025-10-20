import re


def parse_nl_query(q: str) -> dict:
    q_lower = q.lower()
    filters = {}
    if 'single word' in q_lower or 'one word' in q_lower:
       filters['word_count'] = 1
    if 'palindrom' in q_lower:
       filters['is_palindrome'] = True
    m = re.search(r'longer than (\d+) character', q_lower)
    if m:
        n = int(m.group(1))
        filters['min_length'] = n + 1
    m2 = re.search(r"contain(?:s|ing)? the letter ([a-z])", q_lower)
    if m2:
        filters['contains_character'] = m2.group(1)
    m3 = re.search(r"containing the letter ([a-z])", q_lower)
    if m3 and 'contains_character' not in filters:
        filters['contains_character'] = m3.group(1)
    m4 = re.search(r"containing\s+([a-z])([^a-z]|$)", q_lower)
    if m4 and 'contains_character' not in filters:
        filters['contains_character'] = m4.group(1)
    if not filters:
       raise ValueError('Unable to parse natural language query')
    return filters