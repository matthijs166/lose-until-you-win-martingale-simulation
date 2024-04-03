from decimal import Decimal

# a function that wil generate a list with from until with step
def frange(start, stop, step):
    i = []
    i.append(start)
    while i[-1] < stop:
        new_number = Decimal(str(i[-1])) + Decimal(str(step))
        i.append(float(new_number))
    return i