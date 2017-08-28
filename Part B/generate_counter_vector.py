import gzip
import json
import pickle
import os


def get_sentences():
    root = '/opt/nlp_lab/Part A/Json stories'
    for dir in os.listdir(root):
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


def main():
    features = set()

    for sentence in get_sentences():
        for index, char in enumerate(sentence):
            features.add(char)
            if index < len(sentence) - 1:
                features.add(char + sentence[index + 1])
            if index < len(sentence) - 2:
                features.add(char + sentence[index + 1] + sentence[index + 2])

    vector = {feature: index for index, feature in enumerate(features)}


    with open('feature_vector.pickle.gz', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(vector)))


if __name__ == '__main__':
    main()
