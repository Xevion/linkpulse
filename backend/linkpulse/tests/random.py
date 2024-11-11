import random
import string
import time


def epoch() -> int:
    return int(time.time())


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_email() -> str:
    return random_string() + str(epoch()) + "@example.com"
