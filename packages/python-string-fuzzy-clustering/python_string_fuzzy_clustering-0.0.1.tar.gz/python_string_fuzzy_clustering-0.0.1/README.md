# SGFCMedParallel
A Python library for fuzzy clustering of strings using String Grammar Fuzzy C-Medians with multiprocessing.

## Features
- Perform fuzzy clustering on strings using Levenshtein distance

- Update cluster prototypes via modified median string computation

- Accelerate computations using multiprocessing

- Retrieve fuzzy membership matrix and cluster prototypes

- Predict nearest cluster (crisp clustering) for new strings

## Installation
Clone this repository and install using pip:

```bash
pip install .
## Usage
from sgfcmed import SGFCMedParallel  

# Example string dataset
strings = ["cat", "bat", "rat", "mat", "hat"]

# Initialize clustering model
model = SGFCMedParallel(C=2, m=2.0, max_iter=50)

# Fit model to data
model.fit(strings)

# Get fuzzy membership matrix
print("Membership Matrix:", model.membership())

# Get cluster prototype strings
print("Prototypes:", model.prototypes())

# Predict cluster assignments
print("Predictions:", model.predict(["bat", "hat", "sat"]))