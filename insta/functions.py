import re


def validateEmail(email):
    if len(email) > 6:
        if re.match('\A(?P<name>[\w\-_]+)@(?P<domain>[\w\-_]+).(?P<toplevel>[\w]+)\Z', email) is not None:
            return True
    return False
