from itertools import chain


def get_range(n, middle=False):
    # 1D
    if middle:
        return tuple(range(-n, n + 1))
    else:
        return tuple(chain(range(-n, 0), range(1, n + 1)))


def from_ruleset(rule_str):
    rule_str = rule_str.replace(" ", "")
    rule_str = rule_str.strip()
    rules = rule_str.split(",")

    r = 0
    c = 0
    m = False
    s = []
    b = []

    for x in rules:
        if x[0] == "R":
            r = int(x[1:])
        if x[0] == "C":
            c = int(x[1:])
        if x[0] == "M":
            m = bool(int(x[1:]))
        if x[0] == "S":
            s.append(int(x[1:]))
        if x[0] == "B":
            b.append(int(x[1:]))

    neighbourhood = get_range(r, m)
    ruleset = {i: -1 for i in range(2 * r + (1 if m else 0) + 1)}

    for surv in s:
        ruleset[surv] = 0
    for born in b:
        ruleset[born] = 1

    return neighbourhood, ruleset


class Neighbourhoods1D:
    DEFAULT = get_range(1)
    ABACUS = get_range(2, True)
    CLASS_4A = get_range(2, True)
    DATE_PALM = get_range(5, True)


class Rules1D:
    DEFAULT = {
        0: -1,
        1: 1,
        2: -1
    }
    ABACUS = {
        0: 1,
        1: 0,
        2: -1,
        3: 1,
        4: -1,
        5: -1
    }
    CLASS_4A = {
        0: -1,
        1: 0,
        2: 1,
        3: 1,
        4: 1,
        5: -1
    }
    DATE_PALM = {
        0: 1,
        1: -1,
        2: -1,
        3: -1,
        4: -1,
        5: -1,
        6: -1,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
    }


class Rulesets:
    TULIPS = "R10,C0,M1,S0,S3,S6,S10,S11,S14,S15,S16,S17,S18,S19,S20,S21,B1,B11,B12,B17,B18,B19,B20,B21"
    THE_CITY = "R3,C0,M0,S0,S3,B0,B4"
    ROOTS = "R4,C0,M1,S1,S2,S5,S6,S9,B3,B4,B6"
