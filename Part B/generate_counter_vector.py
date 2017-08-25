import gzip
import pickle
import os


def main():
    if not os.path.isfile('chars_set.pickle'):
        raise RuntimeError('missing file chars_set.pickle')

    with open('chars_set.pickle', 'rb') as fp:
        chars = pickle.load(fp)

    vector = dict()
    index = 0

    for char in chars:
        vector[char] = index
        index += 1
        for char2 in chars:
            vector[char + char2] = index
            index += 1
            for char3 in chars:
                vector[char + char2 + char3] = index
                index += 1

    with open('feature_vector.pickle.gz', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(vector)))


if __name__ == '__main__':
    main()
