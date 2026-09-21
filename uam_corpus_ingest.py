import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

class UAMCorpusIngest:
    TRANSITIVITY_FIELD_MAP = {
        'material': 0.85, 'behavioural': 0.40, 'mental': -0.30,
        'verbal': -0.55, 'relational-attributive': 0.10,
        'relational-identifying': 0.25, 'existential': -0.75,
    }