"""Time-ordered splits. There is deliberately no random split in this package.

Shuffling time-series rows lets a model "see" the hours right next to each
test hour, which inflates accuracy. Here train comes first, then validation,
then test, with a gap of `horizon` steps between them so that no forecast is
ever made from a model that was trained on later data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from .features import LeakageError


@dataclass
class Split:
    train: np.ndarray  # boolean masks over the usable rows
    val: np.ndarray
    test: np.ndarray
    gap: pd.Timedelta
    bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]

    def sizes(self) -> Dict[str, int]:
        return {"train": int(self.train.sum()), "val": int(self.val.sum()), "test": int(self.test.sum())}


def time_split(index: pd.DatetimeIndex, fractions=(0.7, 0.15, 0.15), gap: pd.Timedelta = pd.Timedelta(0)) -> Split:
    if not index.is_monotonic_increasing:
        raise ValueError("Rows must be in time order before splitting.")
    f_train, f_val, f_test = fractions
    if min(fractions) <= 0 or abs(f_train + f_val + f_test - 1) > 1e-6:
        raise ValueError("fractions must be three positive numbers that add up to 1, e.g. (0.7, 0.15, 0.15).")
    n = len(index)
    n_train, n_val = int(n * f_train), int(n * f_val)
    if n_train < 2 or n_val < 1 or n - n_train - n_val < 1:
        raise ValueError(f"Not enough rows ({n}) to split into train, validation and test.")
    t_train_end = index[n_train - 1]
    t_val_end = index[n_train + n_val - 1]
    train = np.asarray(index <= t_train_end)
    val = np.asarray((index > t_train_end + gap) & (index <= t_val_end))
    test = np.asarray(index > t_val_end + gap)
    if not val.any() or not test.any():
        raise ValueError("The gap between sets is too large for this much data; use more data or a shorter horizon.")
    split = Split(train, val, test, gap, {
        "train": (index[train][0], index[train][-1]),
        "val": (index[val][0], index[val][-1]),
        "test": (index[test][0], index[test][-1]),
    })
    assert_chronological(split)
    return split


def assert_chronological(split: Split) -> None:
    b = split.bounds
    if not (b["train"][1] + split.gap < b["val"][0] and b["val"][1] + split.gap < b["test"][0]):
        raise LeakageError(f"Sets overlap in time or the gap is too small: {b}")
