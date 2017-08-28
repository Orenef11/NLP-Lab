import gzip
import json
import math
import random
import pickle
import os
from multiprocessing import Pool
from sklearn import svm


def classify(training_positives, training_negatives, testing_positives, testing_negatives):
    training_x = training_positives + training_negatives
    training_y = [1] * len(training_positives) + [0] * len(training_negatives)
    testing_x = testing_positives + testing_negatives
    testing_y = [1] * len(testing_positives) + [0] * len(testing_negatives)

    print('using {0} data points: {1} positives, and {2} negatives'.format(len(training_x), len(training_positives),
                                                                           len(training_negatives)))

    # train
    print('train')
    clf = svm.LinearSVC()
    clf.fit(training_x, training_y)

    # test
    print('test')
    return clf.score(testing_x, testing_y)


def fold(pack):
    positive_slices, negative_slices, i = pack
    print('prepare {0}'.format(i))
    training_positives = []
    training_negatives = []
    testing_positives = []
    testing_negatives = []

    for j in range(10):
        if j != i:
            training_positives.extend(positive_slices[j])
            training_negatives.extend(negative_slices[j])
        else:
            testing_positives = positive_slices[j]
            testing_negatives = negative_slices[j]
    print('classify {0}'.format(i))
    result = classify(training_positives, training_negatives, testing_positives, testing_negatives)
    print(result)
    return result


def main():
    multi_process = True
    # load source and translation vectors
    print('load source and translation vectors')
    with open('source_feature_vectors.pickle.gz', 'rb') as fp:
        source_feature_vectors = pickle.loads(gzip.decompress(fp.read()))
    with open('translation_feature_vectors.pickle.gz', 'rb') as fp:
        translation_feature_vectors = pickle.loads(gzip.decompress(fp.read()))

    # split into 10 slices
    print('split into 10 slices')
    slice_size = len(source_feature_vectors) / 10
    positive_slices = [source_feature_vectors[math.ceil(i * slice_size):math.floor((i + 1) * slice_size)] for i in range(10)]
    slice_size = len(translation_feature_vectors) / 10
    negative_slices = [translation_feature_vectors[math.ceil(i * slice_size):math.floor((i + 1) * slice_size)] for i in range(10)]

    # 10 fold
    print('10 fold')
    packed = zip([positive_slices] * 10, [negative_slices] * 10, range(10))

    if multi_process:
        # multi-process mode
        with Pool(10) as p:
            results = p.map(fold, packed)
    else:
        # single-process mode
        results = []
        for pack in packed:
            results.append(fold(pack))

    total_resilt = 0
    for result in results:
        total_resilt += result

    total_resilt /= 10.0
    print('total result {0}'.format(total_resilt))

if __name__ == '__main__':
    main()
