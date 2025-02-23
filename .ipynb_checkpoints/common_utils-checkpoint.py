from difflib import SequenceMatcher

def score_string(user_input, correct_answer):
    """
    Egyszerű megközelítés STRING típusú kérdés pontozására:
    Ha a két string pontosan egyezik (kis-/nagybetű független),
    akkor 100%-ot adunk, különben a SequenceMatcher arányát szorozzuk meg 100-zal.
    Ha az arány legalább 0.98, akkor 100%-ot adunk.
    """
    s1 = user_input.lower()
    s2 = correct_answer.lower()
    ratio = SequenceMatcher(None, s1, s2).ratio()
    if ratio >= 0.98:
        return 100
    return round(ratio * 100, 2)
