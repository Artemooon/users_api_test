import re


def validate_email(email):
    email_pattern = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r"|^\"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*\""
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9\[\]])?\.)+[A-Z|0-9]{2,}\.?$', re.IGNORECASE)

    if re.match(email_pattern, email):
        return True

    return False

