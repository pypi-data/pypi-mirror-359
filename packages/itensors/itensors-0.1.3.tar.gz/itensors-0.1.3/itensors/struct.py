import uuid
from dataclasses import dataclass, field
from typing import List

import numpy as np
from ncon import ncon


@dataclass(frozen=True)
class Index:
    dimension: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass()
class ITensor:
    tensor: np.array
    indices: List[Index]

    def __post_init__(self):
        assert list(self.tensor.shape) == [i.dimension for i in self.indices]

    def __mul__(self, other):
        shared_indices = [i for i in self.indices if i in other.indices]
        kept_indices = [i for i in self.indices if i not in other.indices] + [i for i in other.indices if
                                                                              i not in self.indices]
        contracted_tensor = ncon(
            [self.tensor, other.tensor],
            [
                [(1 + shared_indices.index(k)) if k in shared_indices else -1 * (1 + kept_indices.index(k)) for k in
                 self.indices],
                [(1 + shared_indices.index(k)) if k in shared_indices else -1 * (1 + kept_indices.index(k)) for k in
                 other.indices],
            ]
        )  # TODO: Handle product of various tensors with the __mul__ notation
        return ITensor(contracted_tensor, kept_indices)
