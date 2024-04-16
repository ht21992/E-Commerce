import uuid
import random
import string


def get_random_code() -> str:
    """
    This function is responsible for creating a random slug

    Returns:
        string: a code
    """
    code = str(uuid.uuid4())[:8].replace("-", "").lower()
    return code


def get_random_string() -> str:
    char_set = string.ascii_uppercase + string.digits
    return "".join(random.sample(char_set * 6, 6))
