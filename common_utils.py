"""
Ez a file csak a score_string függvény minimalista verzióját tartalmazza,
ami a STRING típusú kérdésekhez ad pontszámot.
Lehet persze bonyolítani, attól függően, hogy milyen logikát szeretnél.
"""

def score_string(user_input: str, correct_answer: str) -> float:
    """
    Adjon vissza egy 0-100 közötti pontszámot, aszerint,
    hogy mennyire közelíti meg a user_input a correct_answer-t.
    Itt egy egyszerű hasonlósági példa:
    """
    user_input = user_input.lower()
    correct_answer = correct_answer.lower()

    # Ha teljesen egyezik
    if user_input == correct_answer:
        return 100.0

    # Ha nem, adjunk valami arányos pontot.
    # Pl. (találat hossza / teljes hossza) * 100
    # Minimális példa:
    matches = 0
    for i in range(min(len(user_input), len(correct_answer))):
        if user_input[i] == correct_answer[i]:
            matches += 1

    ratio = matches / max(len(user_input), len(correct_answer))
    return round(ratio * 100, 2)
