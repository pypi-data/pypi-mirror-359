#!/usr/bin/env python3
# this_file: src/uubed/api.py
"""High-level API for uubed encoding."""

from typing import Union, List, Literal, Optional
import numpy as np
from .encoders import eq64, shq64, t8q64, zoq64

EncodingMethod = Literal["eq64", "shq64", "t8q64", "zoq64", "auto"]


def encode(
    embedding: Union[List[int], np.ndarray, bytes],
    method: EncodingMethod = "auto",
    **kwargs
) -> str:
    """
    Encode embedding vector using specified method.

    Args:
        embedding: Vector to encode (bytes or 0-255 integers)
        method: Encoding method or "auto" for automatic selection
        **kwargs: Method-specific parameters

    Returns:
        Encoded string

    Example:
        >>> import numpy as np
        >>> embedding = np.random.randint(0, 256, 32, dtype=np.uint8)
        >>>
        >>> # Full precision
        >>> full = encode(embedding, method="eq64")
        >>>
        >>> # Compact similarity hash
        >>> compact = encode(embedding, method="shq64")
        >>>
        >>> # Sparse top-k representation
        >>> sparse = encode(embedding, method="t8q64", k=8)
    """
    # Convert to list of integers
    if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()
    elif isinstance(embedding, bytes):
        embedding = list(embedding)

    # Validate input
    if not all(0 <= x <= 255 for x in embedding):
        raise ValueError("Embedding values must be in range 0-255")

    # Auto-select method based on use case
    if method == "auto":
        if len(embedding) <= 32:
            method = "shq64"  # Compact for small embeddings
        else:
            method = "eq64"   # Full precision for larger ones

    # Dispatch to appropriate encoder
    if method == "eq64":
        return eq64.eq64_encode(embedding)
    elif method == "shq64":
        planes = kwargs.get("planes", 64)
        return shq64.simhash_q64(embedding, planes=planes)
    elif method == "t8q64":
        k = kwargs.get("k", 8)
        return t8q64.top_k_q64(embedding, k=k)
    elif method == "zoq64":
        return zoq64.z_order_q64(embedding)
    else:
        raise ValueError(f"Unknown encoding method: {method}")


def decode(encoded: str, method: Optional[EncodingMethod] = None) -> bytes:
    """
    Decode encoded string back to bytes.

    Args:
        encoded: Encoded string
        method: Encoding method (auto-detected if None)

    Returns:
        Original bytes

    Note: Only eq64 supports full decoding. Other methods
    are lossy compressions.
    """
    # Auto-detect method from string pattern
    if method is None:
        if "." in encoded:
            method = "eq64"
        else:
            # Cannot auto-detect between compressed formats
            raise ValueError(
                "Cannot auto-detect encoding method. "
                "Please specify method parameter."
            )

    if method == "eq64":
        return eq64.eq64_decode(encoded)
    else:
        raise NotImplementedError(
            f"Decoding not supported for {method}. "
            "These are lossy compression methods."
        )