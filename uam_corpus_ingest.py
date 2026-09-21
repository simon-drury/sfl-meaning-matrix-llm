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

    def __init__(self, corpus_root):
        self.corpus_root = Path(corpus_root)

    def parse_layer(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        units = []
        for segment in root.findall('.//segment'):
            start = int(segment.get('start', 0))
            end = int(segment.get('end', 0))
            features = [f.strip() for f in segment.get('features', '').split(';') if f.strip()]
            units.append({'start': start, 'end': end, 'features': features})
        return units

    def project_to_matrix(self, trans_feats, mood_feats, theme_feats):
        m = np.zeros((3, 3), dtype=np.float32)
        for f in trans_feats:
            f_low = f.lower()
            if f_low in self.TRANSITIVITY_FIELD_MAP:
                m[0, 0] = self.TRANSITIVITY_FIELD_MAP[f_low]
        for f in mood_feats:
            f_low = f.lower()
            if f_low in self.MOOD_TENOR_MAP:
                m[1, 0] = self.MOOD_TENOR_MAP[f_low]
        for f in theme_feats:
            f_low = f.lower()
            if f_low in self.THEME_MODE_MAP:
                m[2, 0] = self.THEME_MODE_MAP[f_low]
        return np.clip(m, -1.0, 1.0)