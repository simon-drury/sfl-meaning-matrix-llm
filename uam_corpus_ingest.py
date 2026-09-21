import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

class UAMCorpusIngest:
    TRANSITIVITY_FIELD_MAP = {
        'material': 0.85, 'behavioural': 0.40, 'mental': -0.30,
        'verbal': -0.55, 'relational-attributive': 0.10,
        'relational-identifying': 0.25, 'existential': -0.75,
    }
    MOOD_TENOR_MAP = {
        'declarative': 0.35, 'interrogative-polar': -0.40,
        'interrogative-wh': -0.60, 'imperative': -0.85,
    }
    THEME_MODE_MAP = {
        'textual-theme': 0.50, 'interpersonal-theme': 0.65,
        'topical-theme': 0.90, 'rheme': -0.40,
    }