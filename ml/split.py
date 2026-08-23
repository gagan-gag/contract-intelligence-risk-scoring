"""Dataset splitting utilities.

The project uses a fixed random seed policy for reproducible training, validation,
and test splits.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def create_split(records: Iterable[Any], train: float = 0.7, val: float = 0.15) -> Dict[str, List[Any]]:
    """Split a collection of records into train/validation/test partitions.

    Args:
        records: Iterable of records to split.
        train: Fraction for the training set.
        val: Fraction for the validation set.

    Returns:
        A dictionary with keys ``train``, ``val``, and ``test``.
    """
    if not 0 < train < 1:
        raise ValueError("train must be between 0 and 1")
    if not 0 < val < 1:
        raise ValueError("val must be between 0 and 1")

    items = list(records)
    if not items:
        return {"train": [], "val": [], "test": []}

    total = len(items)
    train_count = int(total * train)
    val_count = int(total * val)
    test_count = total - train_count - val_count

    if test_count < 0:
        raise ValueError("train + val must be less than 1")

    train_items = items[:train_count]
    val_items = items[train_count : train_count + val_count]
    test_items = items[train_count + val_count :]

    return {"train": train_items, "val": val_items, "test": test_items}
