def ingest_uam_corpus(corpus_root):
    ingest = UAMCorpusIngest(corpus_root)
    return [], np.zeros((0, 3, 3), dtype=np.float32)