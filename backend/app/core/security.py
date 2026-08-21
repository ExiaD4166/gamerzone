from pwdlib import PasswordHash

# PasswordHash.recommended() picks the algorithm currently considered best practice
# (Argon2id). Keeping it behind this module means that when the recommendation
# changes, only this file changes - nothing else in the app knows or cares which
# algorithm is in use.
_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Turn a plain password into a storable hash.

    The result is one-way: there is no function anywhere that converts it back.
    A random salt is generated per call and embedded in the returned string, so
    two users with the same password still get completely different hashes.
    """
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a login attempt against a stored hash.

    The stored hash carries its own salt and parameters, so this re-hashes the
    attempt the same way and compares - the original password is never recovered.
    """
    return _password_hash.verify(plain_password, hashed_password)
