import math
import re


_PREFIXES_2 = {0: "",
               1: "ki", 2: "Mi", 3: "Gi", 4: "Ti", 5: "Pi",
               6: "Ei", 7: "Zi", 8: "Yi", 9: "Ri", 10: "Qi",
               }
_PREFIXES = {0: "",
             -1: "m", -2: "µ", -3: "n", -4: "p", -5: "f",
             -6: "a", -7: "z", -8: "y", -9: "r", -10: "q",
             1: "k", 2: "M", 3: "G", 4: "T", 5: "P",
             6: "E", 7: "Z", 8: "Y", 9: "R", 10: "Q",
             }

VERBOSE = False


def unitprint_block(value, /, unit=None, power=None):
    """
    Format a number to engineering units and prefixes.
    Special padding for cell-like output
    """

    if unit is None:
        unit = " "
    original_value = value
    sign = " "

    if VERBOSE:
        print(f"value = {repr(value)}")
        print(f"unit  = {repr(unit)}")
        print(f"power = {repr(power)}")

    log1000 = 0
    if value != 0:
        if value < 0:
            VERBOSE and print("value negative, flipping sign")
            sign = "-"
            value *= -1
        log1000 = math.log10(value) // (3 * (power if power is not None else 1))
        value *= 1000 ** (-log1000 * (power if power is not None else 1))
        if VERBOSE:
            print(f"log1000 = {log1000}")
            print(f"value w/o log1000 = {value}")
            print()
            print(f"original_value = {original_value}")
            print(f"value (total)  = {value * 1000 ** log1000}")

    if abs(log1000) > 10:
        VERBOSE and print(f"log1000 (={log1000}) > 10\n")
        return f"{sign}{f'{abs(original_value):.3e}': >7}{unit}"

    prefix = _PREFIXES[log1000]

    VERBOSE and print(f"prefix = {prefix}")

    return (f"{sign}{f'{value:.3f}'.rjust(4 + 3 * (power if power is not None else 1))} " 
            f"{prefix or ' '}{unit}{(f'^{power}' if power is not None else '')}")


def unitprint(value, /, unit=None, power=None):
    """
    Format a number to engineering units and prefixes.
    """

    if unit is None:
        unit = " "
    original_value = value
    sign = " "

    if VERBOSE:
        print(f"value = {repr(value)}")
        print(f"unit  = {repr(unit)}")
        print(f"power = {repr(power)}")

    log1000 = 0
    if value != 0:
        if value < 0:
            VERBOSE and print("value negative, flipping sign")
            sign = "-"
            value *= -1
        log1000 = math.log10(value) // (3 * (power if power is not None else 1))
        value *= 1000 ** (-log1000 * (power if power is not None else 1))
        if VERBOSE:
            print(f"log1000 = {log1000}")
            print(f"value w/o log1000 = {value}")
            print()
            print(f"original_value = {original_value}")
            print(f"value (total)  = {value * 1000 ** log1000}")

    if abs(log1000) > 10:
        VERBOSE and print(f"log1000 (={log1000}) > 10\n")
        return f"{sign}{f'{abs(original_value):.3e}': >7}{unit}"

    prefix = _PREFIXES[log1000]

    VERBOSE and print(f"prefix = {prefix}")

    return (f"{value:.3f} {prefix}{unit}" \
            f"{(f'^{power}' if power is not None else '')}")


def unitprint2(value, /, unit=None):
    """
    Format a number to engineering units and prefixes, base2
    Does not support exponents < 0 and values < 1, except for 0
    If there is no prefix large enough to suit the number, 
    the prefix will consist of n equal Factors 
    determined by the prefix P in the format "Pn",
    meaning 1.000 Ei2 is equivalent to 1*1024**(6*2)
    """

    if unit is None:
        unit = " "
    original_value = value
    sign = " "

    if VERBOSE:
        print(f"value = {repr(value)}")
        print(f"unit  = {repr(unit)}")

    log1024 = 0
    if value != 0:
        if value < 0:
            raise ValueError(
                "Negative base2 units are not supported "
                "(it doesn't make sense to have negative bytes)"
                )
        log1024 = max(math.log2(value), 0) // 10
        value *= 1024 ** (-log1024)
        if VERBOSE:
            print(f"log1024 = {log1024}")
            print(f"value w/o log1000 = {value}")
            print()
            print(f"original_value = {original_value}")
            print(f"value (total)  = {value * 1024 ** log1024}")


    if log1024 > 10:
        for i in range(10, 0, -1):
            VERBOSE and print(f"log1024 % {i} = {log1024 % i}")
            if log1024 % i == 0:
                prefix = i
                break
        return f"{value:.3f} {_PREFIXES_2[prefix]}{log1024 // prefix:.0f}{unit}"

    prefix = _PREFIXES_2[log1024]

    VERBOSE and print(f"prefix = {prefix}")

    if prefix == "":
        return f"{math.ceil(value):0.0f} {unit}"

    return f"{value:.3f} {prefix}{unit}"


def unitprint2_block(value, /, unit=None):
    """
    Format a number to engineering units and prefixes, base2
    Does not support exponents < 0 and values < 1, except for 0
    If there is no prefix large enough to suit the number, 
    the prefix will consist of n equal Factors 
    determined by the prefix P in the format "Pn",
    meaning 1.000 Ei2 is equivalent to 1*1024**(6*2)
    """

    if unit is None:
        unit = " "
    original_value = value

    if VERBOSE:
        print(f"value = {repr(value)}")
        print(f"unit  = {repr(unit)}")

    sign = " "
    log1024 = 0
    if value != 0:
        if value < 0:
            raise ValueError(
                "Negative base2 units are not supported "
                "(it doesn't make sense to have negative or half bytes)"
                )
        log1024 = max(math.log2(value), 0) // 10
        value *= 1024 ** (-log1024)
        if VERBOSE:
            print(f"log1024 = {log1024}")
            print(f"value w/o log1000 = {value}")
            print()
            print(f"original_value = {original_value}")
            print(f"value (total)  = {value * 1024 ** log1024}")

    if log1024 > 10:
        for i in range(10, 0, -1):
            VERBOSE and print(f"log1024 % {i} = {log1024 % i}")
            if log1024 % i == 0:
                prefix = i
                break
        return f"{value:7.3f} {_PREFIXES_2[prefix]}{log1024 // prefix:.0f}{unit}"

    prefix = _PREFIXES_2[log1024]

    VERBOSE and print(f"prefix = {prefix}")

    if prefix == "":
        return f"{ceil(value):0.0f}   {unit or ' '}"

    return f"{value:7.3f} {prefix}{unit or ' '}"


def number_converter(strin: str, /, power=1, _avoid_recursion_again=False):
    """Returns a float from a number like 5k6 -> 5.6e3"""

    letters = {-1: "m", -2: "u", -3: "n", -4: "p", -5: "f", -6: "a",
               1: "k",  2: "meg",  3: "gig",  4: "ter",  5: "pet",  6: "ex"}
    result_letter = "."
    result_exponent = 0
    VERBOSE and print()
    for exponent, letter in letters.items():
        VERBOSE and print(f"{letter} (=10**{exponent * 3}) in {strin} == {letter in strin}")
        if letter in strin:
            result_letter = letter
            result_exponent = exponent
            break
    VERBOSE and print()
    if result_exponent == 0:
        VERBOSE and print("exponent == 0")
        reg = re.match(r"(\d*\.\d+|\d+\.?\d*)e(\d+)", strin)
        VERBOSE and print(f"regex: {reg} ({reg and reg.group()}")
        if reg:
            return float(strin)
        else:
            return None

    if not "".join(strin.split(result_letter)).isnumeric():
        # Heck me recursion
        VERBOSE and print(re.search(r"\.\d+\D*\d", strin))
        if re.search(r"\.\d+\D*\d", strin):
            return None
        if not _avoid_recursion_again and (res := number_converter(
                strin
                .replace(result_letter, "", 1)
                .replace(".", result_letter, 1),
                _avoid_recursion_again=True
            )) is not None:
            return res
        return None

    return (
        float( ".".join(strin.split(result_letter)) )
        * 1000**(result_exponent*power)
    )
