from pymongo import MongoClient, errors
from pprint import pprint
import json

client = MongoClient()
db = client.web_parser
collection = db.pikabu
# collection = db.dzen


# def load_to_file(story: dict, filename: str = 'pikabu_stories.txt'):
# def load_to_file(story: dict, filename: str = 'dzen_stories.txt'):
def load_to_file(story: dict, filename: str = 'all_stories.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        line = json.dumps(story, ensure_ascii=False)
        f.write(f'{line}\n')


def create_dataset(filename: str = 'all_stories.txt'):
    with open(filename, 'a', encoding='utf-8') as f:

        collection = db.pikabu
        for i in collection.find({}, {"content": 1, "_id": 0}):
            if len(i["content"]) > 300:
                f.write(f'{i["content"]}\n')

        collection = db.dzen
        for i in collection.find({}, {"content": 1, "_id": 0}):
            if len(i["content"]) > 300:
                f.write(f'{i["content"]}\n')


def delete_all():
    collection.delete_many({})


def clear_files():
    try:
        file = open('pikabu_stories.txt', 'w')
        file.close()
    except FileNotFoundError:
        pass
    except Exception as e:
        pass


def find():
    for i in collection.find({"tags": "Граффити"}, {"_id": 0, "content": 0}):
        pprint(i)


def find_all():
    for i in collection.find({}, {"_id": 0, "content": 0}):
        pprint(i)


def count():
    print(collection.count())


if __name__ == "__main__":
    delete_all()
    # count()
    # clear_files()
    create_dataset()
