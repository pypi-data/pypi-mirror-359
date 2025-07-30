def alphanumeric_to_snake_case(name: str) -> str:
    """
    convert a string to snake case https://learn.microsoft.com/en-us/visualstudio/code-quality/ca1709?view=vs-2022
    "By convention, two-letter acronyms use all uppercase letters,
    and acronyms of three or more characters use Pascal casing."
    """
    if len(name) == 0:
        return ""
    if name[0].isnumeric():
        raise ValueError(f"{name=} can't start with a number")
    if any([not c.isalnum() for c in name]):
        raise ValueError(f"{name=} has to be alphanumeric")
    result = [name[0].lower()]
    i = 1
    while i < len(name):
        if not name[i].isupper():
            result += [name[i]]
            i += 1
            continue
        # encountered upper case letter:
        # - 1 upper case letter: (ThisIsAtest -> this_is_atest)
        # - 2 upper case letter: (ThisIsATest -> this_is_a_test)
        # - 3 upper case letter: (ThisIsABTest -> this_is_ab_test)
        # check if last letter -> always lower (ThisIsTestA -> this_is_test_a)
        if i == len(name) - 1:
            result += ["_", name[i].lower()]
            break
        # check for 1 upper case letter (ThisIsTest -> this_is_test)
        if i < len(name) - 1 and not name[i + 1].isupper():
            result += ["_", name[i].lower()]
            i += 1
            continue
        # check if last 2 letters are upper case -> always lower (ThisIsTestAB -> this_is_test_ab)
        if i == len(name) - 2 and name[i + 1].isupper():
            result += ["_", name[i].lower(), name[i + 1].lower()]
            break
        # check for 2 upper case letter (ThisIsATest -> this_is_a_test)
        if i < len(name) - 2 and name[i + 1].isupper() and not name[i + 2].isupper():
            result += ["_", name[i].lower(), "_", name[i + 1].lower()]
            i += 2
            continue
        # check if last 3 letters are upper case -> invalid (ThisIsTestABC should be ThisIsTestAbc)
        if i == len(name) - 3 and name[i + 1].isupper() and name[i + 2].isupper():
            raise ValueError(f"can't have 3 upper case letters at the end of '{name}'")
        # check for 3 upper case letter (ThisIsABTest -> this_is_ab_test)
        if i < len(name) - 3 and name[i + 1].isupper() and name[i + 2].isupper() and not name[i + 3].isupper():
            result += ["_", name[i].lower(), name[i + 1].lower(), "_", name[i + 2].lower()]
            i += 3
            continue
        # check for 4 upper case letters (ThisIsABCTest -> should be ThisIsAbcTest)
        if i < len(name) - 3 and name[i + 1].isupper() and name[i + 2].isupper() and name[i + 3].isupper():
            raise ValueError(f"can't have 4 upper case letters in a row '{name}'")
    return "".join(result)
