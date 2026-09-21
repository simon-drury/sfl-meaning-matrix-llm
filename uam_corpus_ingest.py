import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

class UAMCorpusIngest:
    TRANSITIVITY_FIELD_MAP={'material':.85,'behavioural':.4,'mental':-.3,'verbal':-.55,'relational-attributive':.1,'relational-identifying':.25,'existential':-.75}
    MOOD_TENOR_MAP={'declarative':.35,'interrogative-polar':-.4,'interrogative-wh':-.6,'imperative':-.85}
    THEME_MODE_MAP={'textual-theme':.5,'interpersonal-theme':.65,'topical-theme':.9,'rheme':-.4}
    def __init__(self,root):
        self.corpus_root=Path(root)
    def parse_layer(self,path):
        root=ET.parse(path).getroot()
        return [{'start':int(s.get('start',0)),'end':int(s.get('end',0)),'features':[f.strip() for f in s.get('features','').split(';') if f.strip()]} for s in root.findall('.//segment')]
    def project_to_matrix(self,trans,mood,theme):
        m=np.zeros((3,3),dtype=np.float32)
        for f in trans:
            if f.lower() in self.TRANSITIVITY_FIELD_MAP:m[0,0]=self.TRANSITIVITY_FIELD_MAP[f.lower()]
        for f in mood:
            if f.lower() in self.MOOD_TENOR_MAP:m[1,0]=self.MOOD_TENOR_MAP[f.lower()]
        for f in theme:
            if f.lower() in self.THEME_MODE_MAP:m[2,0]=self.THEME_MODE_MAP[f.lower()]
        return np.clip(m,-1,1)
def ingest_uam_corpus(root):
    return [],np.zeros((0,3,3),dtype=np.float32)