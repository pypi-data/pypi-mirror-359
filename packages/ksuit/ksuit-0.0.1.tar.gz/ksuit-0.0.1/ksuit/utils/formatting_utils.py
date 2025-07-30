import math

import numpy as np

_SI_PREFIXES = ["", "K", "M", "G", "T", "P", "E"]


def int_to_si_string(number: int, precision: int = 1):
    if number == 0:
        return "{short_number:.{precision}f}".format(short_number=0., precision=precision)
    if number < 0:
        number = -number
        sign = "-"
    else:
        sign = ""

    magnitude = int(np.log10(number) / 3)
    short_number = int(number / (1000**magnitude / 10**precision)) / 10**precision
    return "{sign}{short_number:.{precision}f}{si_unit}".format(
        sign=sign,
        short_number=short_number,
        precision=precision,
        si_unit=_SI_PREFIXES[magnitude],
    )


def float_to_scientific_notation(value: float, max_precision: int, remove_plus: bool = True) -> str:
    if math.isnan(value) or math.isinf(value):
        return str(value)
    # to default scientific notation (e.g. '3.20e-06')
    float_str = "%.*e" % (max_precision, value)
    mantissa, exponent = float_str.split('e')
    # enforce precision
    mantissa = mantissa[:len("0.") + max_precision]
    # remove trailing zeros (and '.' if no zeros remain)
    mantissa = mantissa.rstrip("0").rstrip(".")
    # remove leading zeros
    exponent = f"{exponent[0]}{exponent[1:].lstrip('0')}"
    if len(exponent) == 1:
        exponent += "0"
    if remove_plus and exponent[0] == "+":
        exponent = exponent[1:]
    return f"{mantissa}e{exponent}"


def seconds_to_duration(
    seconds: int,
    largest_unit: str = "day",
    remove_zeros_until_unit: str = "hour"
) -> str:
    total_seconds = seconds
    tenth_milliseconds = int((total_seconds - int(total_seconds)) * 100)
    total_seconds = int(total_seconds)
    seconds = total_seconds % 60
    minutes = total_seconds % 3600 // 60
    hours = total_seconds % 86400 // 3600
    days = total_seconds // 86400
    if largest_unit == "day":
        if remove_zeros_until_unit == "hour":
            if days == 0:
                return f"{hours:02}:{minutes:02}:{seconds:02}.{tenth_milliseconds:02}"
            return f"{days}-{hours:02}:{minutes:02}:{seconds:02}.{tenth_milliseconds:02}"
        else:
            raise NotImplementedError
    if largest_unit == "hour":
        hours += days * 24
        if remove_zeros_until_unit == "hour":
            return f"{hours:02}:{minutes:02}:{seconds:02}.{tenth_milliseconds:02}"
        if remove_zeros_until_unit == "minute":
            if hours == 0:
                return f"{minutes:02}:{seconds:02}.{tenth_milliseconds:02}"
            return f"{hours:02}:{minutes:02}:{seconds:02}.{tenth_milliseconds:02}"
        raise NotImplementedError
    raise NotImplementedError