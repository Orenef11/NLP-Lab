import pickle
import json
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
    chars = set()
    for sentence in get_sentences():
        for char in sentence:
            chars.add(char)
    with open('chars_set.pickle', 'wb') as fp:
        pickle.dump(chars, fp)


if __name__ == '__main__':
    main()