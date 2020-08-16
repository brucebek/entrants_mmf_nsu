import os
import json
import pytz
from datetime import datetime
from entrants import get_article
from config import USERS


def file_open_path(pth):
    def file_wrap(func):
        def wrapper(*args, **kwargs):
            with open(os.path.abspath(pth), 'r+', encoding='utf-8') as f:
                res = func(f, *args, **kwargs)
                return res

        return wrapper

    return file_wrap


def new_dump(data, f):
    f.truncate(0)
    f.seek(0)
    json.dump(data, f, indent=4)


@file_open_path(USERS)
def add_user(users_f, id, username, is_admin=False):
    users = json.load(users_f)
    if id not in users:
        users[id] = {'username': username, 'is_admin': is_admin, 'activity': []}
        os.mkdir(f'{os.path.abspath(f"db/{id}")}')
        new_dump(users, users_f)
        return users[id]


@file_open_path(USERS)
def del_user(users_f, id):
    users = json.load(users_f)
    if id in users:
        user = users[id]
        del users[id]
        os.rmdir(f'{os.path.abspath(f"db/{id}")}')
        new_dump(users, users_f)
        return user


@file_open_path(USERS)
def get_user(users_f, id):
    users = json.load(users_f)
    if id in users:
        return users[id]


@file_open_path(USERS)
def add_activity(users_f, id, act_name):
    users = json.load(users_f)
    tz = pytz.timezone('Asia/Novosibirsk')
    act_time = datetime.now(tz).strftime('%d.%m.%Y %H:%M:%S')
    users[id]['activity'].append({'time': act_time, 'action': act_name})
    new_dump(users, users_f)


def get_activity(id):
    user = get_user(id)
    if user:
        activity = user['activity']
        return activity


def get_path_list(id, direction, name, type_list):
    html = get_article(direction, name, type_list)
    pth = f'{os.path.abspath(f"db/{id}/{name}.html")}'
    with open(pth, 'w', encoding='utf-8') as list_file:
        list_file.write(html)

    return pth


if __name__ == '__main__':
    add_user('291384681', 'bruce0609', is_admin=True)
