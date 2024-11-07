import bcrypt


def gen_hashed_value(value: str, rounds: int = 12) -> str:
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_value = bcrypt.hashpw(value.encode("utf-8"), salt)
    return hashed_value.decode("utf-8")


def check_hashed_value(value: str, hashed: str) -> bool:
    if not value or not hashed:
        return False
    return bcrypt.checkpw(value.encode("utf-8"), hashed.encode("utf-8"))
