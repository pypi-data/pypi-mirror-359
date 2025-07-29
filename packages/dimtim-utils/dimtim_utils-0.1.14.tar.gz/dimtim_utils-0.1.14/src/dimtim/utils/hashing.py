import hashlib
import hmac
from typing import Union


def md5(val: Union[str, bytes]) -> str:
    """
    Calculate the MD5 hash of a string or bytes object.

    Parameters:
        val (Union[str, bytes]): The value to hash.

    Returns:
        str: The hexadecimal representation of the MD5 hash.

    Example:
        >>> hash_value = md5("hello world")
        >>> print(hash_value)  # Output: "5eb63bbbe01eeed093cb22bb8f5acdc3"

    Note:
        MD5 is considered cryptographically broken and should not be used for
        security purposes. Use it only for non-security applications like checksums.
    """
    return hashlib.md5(val if isinstance(val, bytes) else str(val).encode()).hexdigest()


def sha1(val: Union[str, bytes]) -> str:
    """
    Calculate the SHA-1 hash of a string or bytes object.

    Parameters:
        val (Union[str, bytes]): The value to hash.

    Returns:
        str: The hexadecimal representation of the SHA-1 hash.

    Example:
        >>> hash_value = sha1("hello world")
        >>> print(hash_value)  # Output: "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"

    Note:
        SHA-1 is considered cryptographically broken and should not be used for
        security purposes. Use it only for non-security applications.
    """
    return hashlib.sha1(val if isinstance(val, bytes) else str(val).encode()).hexdigest()


def secret_hmac(key: str, message: str) -> str:
    """
    Calculate an HMAC-SHA1 digest for a message using a secret key.

    HMAC (Hash-based Message Authentication Code) provides a way to verify
    both the data integrity and the authenticity of a message.

    Parameters:
        key (str): The secret key for the HMAC.
        message (str): The message to authenticate.

    Returns:
        str: The hexadecimal representation of the HMAC-SHA1 digest.

    Example:
        >>> digest = secret_hmac("secret_key", "message_to_authenticate")
        >>> print(digest)  # Hexadecimal HMAC-SHA1 digest
    """
    return hmac.digest(key.encode('utf8'), str(message).encode('utf8'), 'sha1').hex()
