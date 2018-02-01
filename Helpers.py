def my_hash(o):
    # Used to hash states to keep track of seen states
    try:
        return hash(o)
    except TypeError:
        if type(o) == list:
            return hash(tuple(my_hash(e) for e in o))
