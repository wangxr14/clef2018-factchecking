import pandas as pd
import random
from os.path import dirname, join

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

from format_checker.subtaskB import check_format
from scorer.subtaskB import evaluate

_LABELS = ['TRUE', 'FALSE', 'HALF-TRUE']
_COL_NAMES = ['line_number', 'speaker', 'text', 'claim_number', 'normalized_claim', 'label']

def run_random_baseline(test_debate, random_baseline_fpath):
    gold = pd.read_csv(test_debate, sep='\t', names=_COL_NAMES)

    gold = gold[gold['claim_number'].notna()]
    gold.drop_duplicates(subset=['claim_number', 'label'], inplace=True)
    gold['claim_number'] = gold['claim_number'].astype(int)

    gold['rand_label'] = [random.sample(_LABELS, 1)[0] for _ in range(len(gold))]

    with open(random_baseline_fpath, 'w') as out:
        gold[['claim_number', 'rand_label']].to_csv(out, sep='\t', header=None, index=False)


def run_ngram_baseline(train_debates, test_debate, results_fpath):
    test_df = pd.read_csv(test_debate, sep='\t', names=_COL_NAMES)
    test_df = test_df[test_df['claim_number'].notna()]
    test_df.drop_duplicates(subset=['claim_number', 'label'], inplace=True)
    test_df['claim_number'] = test_df['claim_number'].astype(int)

    train_list = []
    for train_debate in train_debates:
        df = pd.read_csv(train_debate, index_col=None, header=None, names=_COL_NAMES, sep='\t')
        train_list.append(df)
    train_df = pd.concat(train_list)
    train_df = train_df[train_df['claim_number'].notna()]
    train_df.drop_duplicates(subset=['claim_number', 'label'], inplace=True)
    train_df['claim_number'] = train_df['claim_number'].astype(int)

    pipeline = Pipeline([
        ('ngrams', TfidfVectorizer(ngram_range=(1,2))),
        ('clf', RandomForestClassifier(max_features=15, random_state=0))
    ])
    pipeline.fit(train_df['text'], train_df['label'])

    with open(results_fpath, "w") as results_file:
        predicted_labels = pipeline.predict(test_df['text'])
        for claim_num, label in zip(test_df['claim_number'], predicted_labels):
            results_file.write("{}\t{}\n".format(claim_num, label))



if __name__ == '__main__':
    ROOT_DIR = dirname(dirname(__file__))
    gold_data_folder = join(ROOT_DIR, 'data/gold/')

    train_debates = [join(gold_data_folder, 'Task2-English-1st-Presidential.txt'),
                     join(gold_data_folder, 'Task2-English-Vice-Presidential.txt')]
    test_debate = join(gold_data_folder, 'Task2-English-2nd-Presidential.txt')

    random_baseline_fpath = join(ROOT_DIR, 'data/baselines/subtaskB_random_baseline.txt')
    run_random_baseline(test_debate, random_baseline_fpath)
    if check_format(random_baseline_fpath):
        evaluate(test_debate, random_baseline_fpath)

    ngram_baseline_fpath = join(ROOT_DIR, 'data/baselines/subtaskB_ngram_baseline.txt')
    run_ngram_baseline(train_debates, test_debate, ngram_baseline_fpath)

    if check_format(ngram_baseline_fpath):
        evaluate(test_debate, ngram_baseline_fpath)