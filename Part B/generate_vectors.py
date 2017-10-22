import gzip
import json
import random
import pickle
import os


def get_sentences(source=False):
    root = '/opt/nlp_lab/Part A/Json stories'
    source_dir = 'עברית'
    for dir in os.listdir(root):
        if (source and dir == source_dir) or (not source and dir != source_dir):
            dir_path = os.path.join(root, dir)
            for file in os.listdir(dir_path):
                full_path = os.path.join(root, dir, file)
                with open(full_path, 'r', encoding='utf-8') as fp:
                    raw = fp.read()
                    story_json = json.loads(raw)
                if 'Introduction-Text' in story_json:
                    for line in story_json['Introduction-Text'].split('\r\n'):
                        yield line
                if 'Article-text' in story_json:
                    for line in story_json['Article-text'].split('\r\n'):
                        yield line


def get_chunks(lines, k):
    chunks = []
    last_chunk = []
    last_chunk_size = 0
    for line in lines:
        if k < last_chunk_size + len(line):
            chunks.append(last_chunk)
            last_chunk = []
            last_chunk_size = 0

        last_chunk.append(line)
        last_chunk_size += len(line)

    chunks.append(last_chunk)

    return chunks


def init_feature_vector(header_vector):
    return [0] * len(header_vector)


def get_feature_vectors(chunks, header_vector):
    feature_vectors = []

    for chunk in chunks:
        # initialize feature vector
        feature_vector = init_feature_vector(header_vector)

        for line in chunk:
            for index, char in enumerate(line):
                feature_vector[header_vector[char]] += 1
                if index < len(line) - 1:
                    feature_vector[header_vector[char + line[index + 1]]] += 1
                if index < len(line) - 2:
                    feature_vector[header_vector[char + line[index + 1] + line[index + 2]]] += 1
        feature_vectors.append(feature_vector)

    return feature_vectors

def main():
    # chunk size
    k = 1000

    # load the base feature vector
    print('load the base feature vector')
    with open('feature_vector.pickle.gz', 'rb') as fp:
        header_vector = pickle.loads(gzip.decompress(fp.read()))

    # load the line
    print('load the lines')
    source_lines = [line for line in get_sentences(source=True)]
    translation_lines = [line for line in get_sentences(source=False)]

    # suffle the lines
    print('suffle the lines')
    source_lines = random.sample(source_lines, len(source_lines))
    translation_lines = random.sample(translation_lines, len(translation_lines))

    # clump the lines into chunks smaller or equal to k
    print('clump the lines into chunks smaller or equal to k')
    source_chunks = get_chunks(source_lines, k)
    translation_chunks = get_chunks(translation_lines, k)

    # calculate feature vector for each chunk
    print('calculate feature vector for each chunk')
    source_feature_vectors = get_feature_vectors(source_chunks, header_vector)
    translation_feature_vectors = get_feature_vectors(translation_chunks, header_vector)

    # store the feature vectors
    print('store the feature vectors')
    with open('source_feature_vectors.pickle.gz', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(source_feature_vectors)))
    with open('translation_feature_vectors.pickle.gz', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(translation_feature_vectors)))

if __name__ == '__main__':
    main()
