

def number_to_percent(number, precision=2):
    return round(number * 100, precision)


def number_format(number):
    return "{:,}".format(number)