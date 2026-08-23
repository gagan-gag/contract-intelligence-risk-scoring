import json
import random
from pathlib import Path

def create_split(records, train=0.7, val=0.15):
    shuffled = list(records)
    random.seed(42)
    random.shuffle(shuffled)
    n = len(shuffled)
    train_end = int(n * train)
    val_end = train_end + int(n * val)
    return {
        "train": shuffled[:train_end],
        "val": shuffled[train_end:val_end],
        "test": shuffled[val_end:],
    }
