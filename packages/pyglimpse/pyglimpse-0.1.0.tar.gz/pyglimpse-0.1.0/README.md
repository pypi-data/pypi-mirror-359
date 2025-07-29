# pyglimpse

A pandas DataFrame glimpse function inspired by R's dplyr::glimpse.

## Installation

```bash
pip install pyglimpse
```

## Usage

```python
import pandas as pd
from pyglimpse import glimpse

df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': ['x', 'y', 'z']
})
glimpse(df)
``` 