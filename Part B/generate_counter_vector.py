import gzip
import pickle
import os


def main():
    if not os.path.isfile('chars_set.pickle'):
        raise RuntimeError('missing file chars_set.pickle')

    with open('chars_set.pickle', 'rb') as fp:
        chars = pickle.load(fp)

    vector = dict()

    for char in chars:
        vector[char] = 0
        for char2 in chars:
            vector[char + char2] = 0
            for char3 in chars:
                vector[char + char2 + char3] = 0

    with open('counter_vector.pickle.gz', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(vector)))


if __name__ == '__main__':
    main()
