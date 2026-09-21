"""Build matrix trajectories and lexical-boundary datasets from UAM CorpusTool XML."""
import json
import sys
from pathlib import Path
import numpy as np
from uam_corpus_ingest import UAMCorpusIngest

def layer(root, name, stem):
    p = root / 'corpus' / 'layers' / name / (stem + '.xml')
    return UAMCorpusIngest(root).parse_layer(p) if p.exists() else []

def features(units, start, end):
    out = []
    for u in units:
        if u['start'] < end and start < u['end']:
            out.extend(u['features'])
    return sorted(set(out))

def build(corpus_root, output_dir='data'):
    root = Path(corpus_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ingest = UAMCorpusIngest(root)
    matrices, deltas, docs, clauses, lexical = [], [], [], [], []
    text_dir = root / 'corpus' / 'text'
    for text_path in sorted(text_dir.glob('*.txt')):
        text = text_path.read_text(encoding='utf-8')
        stem = text_path.stem
        trans = layer(root, 'transitivity', stem)
        mood = layer(root, 'mood', stem)
        theme = layer(root, 'theme', stem)
        boundaries = sorted({(u['start'], u['end']) for u in trans + mood + theme})
        previous = None
        for clause_id, (start, end) in enumerate(boundaries):
            tf = features(trans, start, end)
            mf = features(mood, start, end)
            thf = features(theme, start, end)
            matrix = ingest.project_to_matrix(tf, mf, thf)
            delta = np.zeros((3, 3), dtype=np.float32) if previous is None else matrix - previous
            span = text[start:end]
            matrices.append(matrix)
            deltas.append(delta)
            docs.append(stem)
            clauses.append(clause_id)
            lexical.append({'document_id': stem, 'clause_id': clause_id, 'source_span': span, 'matrix': matrix.tolist(), 'transitivity': tf, 'mood': mf, 'theme': thf})
            previous = matrix
    np.savez_compressed(out / 'uam_meaning_trajectories.npz', matrices=np.asarray(matrices, dtype=np.float32), deltas=np.asarray(deltas, dtype=np.float32), doc_ids=np.asarray(docs), clause_ids=np.asarray(clauses, dtype=np.int32))
    (out / 'uam_lexical_boundary_index.json').write_text(json.dumps(lexical, ensure_ascii=False, indent=2), encoding='utf-8')
    print('clauses:', len(matrices))
    print('trajectories:', out / 'uam_meaning_trajectories.npz')
    print('boundary index:', out / 'uam_lexical_boundary_index.json')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python build_uam_dataset.py <uam_project_root> [output_dir]')
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'data')
