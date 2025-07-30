from dataclasses import dataclass
import numpy as np

@dataclass()
class ITensor:
    tensor: np.array
