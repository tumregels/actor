import json
import os
import os.path as op
import pickle
import subprocess
import sys
from datetime import datetime, timedelta
from urllib.parse import unquote, urlsplit

from furl import furl
from prompt_toolkit import prompt

from actor import cwd, settings, all_backends, teen_backend_list, army_backend_list


def decode_url(url):
    return unquote(url)


def pk_save(data):
    with open('pending.pickle', 'wb') as f:
        pickle.dump(data, f)


def pk_load():
    with open('pending.pickle', 'rb') as f:
        pending = pickle.load(f)
        return pending


def json_dump(data):
    with open('pending.json', 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)


def json_load(file):
    with open(file, 'r', encoding='utf-8') as data_file:
        data = json.load(data_file)
        return data


def ask_for_confirmation():
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input(os.linesep + "Do you want to open activities ? (y/n)").lower()
    if choice in yes:
        return True
    elif choice in no:
        print('Exiting actor ...')
        sys.exit()
    else:
        print("Please respond with 'yes' or 'no'")
        sys.exit()


def ask_pswd():
    if os.getenv('BEPASS'):
        pswd = os.getenv('BEPASS')
    elif 'pswd' in settings:
        pswd = settings['pswd']
    else:
        pswd = prompt('Password: ', is_password=True)
        settings['pswd'] = pswd
    return pswd


def open_config_file():
    conf_path = op.abspath(op.join(cwd, 'config.txt'))
    subprocess.call(['open', '-a', 'TextEdit', conf_path])


def get_backend(url):
    parsed_url = urlsplit(url)
    return parsed_url.netloc


def remove_from_backend_list(failed_url, urls):
    failed_backend = failed_url.netloc
    all_backends.remove(failed_backend) if failed_backend in teen_backend_list else None
    teen_backend_list.remove(failed_backend) if failed_backend in teen_backend_list else None
    army_backend_list.remove(failed_backend) if failed_backend in army_backend_list else None


def sort_urls_by_activities(urls):
    furls = [furl(url) for url in urls]
    furls_sorted = sorted(furls, key=lambda k: k.query.params.get('filters[activity_title]'))
    urls = [url for url in furls_sorted]
    return urls

def get_dates_from_config(dates):
    date_list = []

    for date in dates:
        if ',' in date:
            start, end = [datetime.strptime(x.strip(), '%Y-%m-%d') for x in date.split(',')]
            dd = [start + timedelta(days=x) for x in range((end - start).days + 1)]
            date_list.extend(dd)
        else:
            date_list.append(datetime.strptime(date, '%Y-%m-%d'))

    date_string_list = [x.strftime('%Y-%m-%d') for x in date_list]
    date_string_list = sorted(date_string_list, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

    return date_string_list