import os
import sys
import time
from collections import OrderedDict, Counter

import requests
from bs4 import BeautifulSoup
from furl import furl
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from actor import settings, logger, session, teen_backend_list
from actor.utils import ask_pswd, get_dates_from_config

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_all_activity_try_urls(backend_list, activity_list, status=0):
    urls = []
    for activity in activity_list:
        for backend in backend_list:
            url = furl('https://{}/'.format(backend))
            url.set(path='/api/activity-try')
            url.set(query_params=OrderedDict([('page', 1),
                                              ('per-page', 100),
                                              ('filters[activity_title]', activity),
                                              ('filters[status][]', status)]))
            urls.append(url)

    return urls


def add_date_filters(urls):
    dates = get_dates_from_config(settings.dates)
    if not dates:
        return urls
    urls_with_date = []
    for url in urls:
        for date in dates:
            urlc = url.copy()
            urlc.args['filters[end_date]'] = date
            urls_with_date.append(urlc)

    return urls_with_date


def get_army_activity_try_urls(backend_list, activity_list, status=0):
    urls = get_all_activity_try_urls(backend_list, activity_list, status)
    for url in urls:
        if 'evnbackend' in url.host:
            url.add({'filters[session]': '09:00'})

    return urls


def get_pending_activities(urls):
    pending = []
    for url in tqdm(urls, desc='Gathering Stats'):
        try:
            r = session.head(url)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print("Connection Error from {}. Continuing ...".format(url.netloc))
            logger.exception(e)
            continue

        total = r.headers.get('X-Pagination-Total-Count')

        if total != '0':
            ract = session.get(url)
            data = ract.json()  # TODO https://stackoverflow.com/questions/43968468/error-when-get-json-from-requests-get
            for item in data:
                item.update({'backend': url.host})
            pending.extend(data)

    return pending


def start_browser():
    """Start chrome browser and return its driver"""
    chrome_options = Options()
    chrome_options.binary_location = settings.get('browser', settings.browser_exe_path)
    chrome_options.add_extension(settings.extension_path)
    chrome_options.add_argument('disable-infobars')

    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": settings.download_path,
        "directory_upgrade": True
    }

    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        executable_path=settings.chromedriver_path,
        chrome_options=chrome_options
    )

    return driver


def login_backends(driver, backend_list):
    for backend in set(backend_list):
        if 'mmbackend' in backend:
            login_backend_via_selenium(driver, backend)
        else:
            login_backend_via_cookies(driver, backend)


def login_backend_via_cookies(driver, backend):
    backend_url = 'https://{}/site/login'.format(backend)
    driver.get(backend_url)
    for c in session.cookies:
        driver.add_cookie({'name': c.name, 'value': c.value,
                           'path': c.path, 'expiry': c.expires})


def wait_for_element_by_name(driver, name):
    element = WebDriverWait(driver, 25).until(lambda x: x.find_element_by_name(name))
    return element


def login_backend_via_selenium(driver, backend):
    backend_url = 'https://{}/site/login'.format(backend)
    driver.get(backend_url)

    pswd = ask_pswd()
    uname = settings['username']

    username = wait_for_element_by_name(driver, 'LoginForm[username]')
    username.send_keys(uname)

    password = wait_for_element_by_name(driver, 'LoginForm[password]')
    password.send_keys(pswd)

    form = wait_for_element_by_name(driver, 'login-button')
    form.click()

    time.sleep(1)


def login_examine(driver):
    examine_url = 'http://examine.tumo.org'
    login_url = examine_url + '/login.php'

    login_data = {
        'username': 'actor',
        'password': 'sRy95e6nyqBl',
        'submit': 'Log+In'
    }

    resp = session.post(login_url, data=login_data, allow_redirects=True, headers=dict(Referer=login_url))
    soup = BeautifulSoup(resp.text, 'html.parser')

    if 'actor' in soup.text:
        print('logged in as actor (examine.tumo.org)')

        driver.get(examine_url)
        for c in session.cookies:
            driver.add_cookie({'name': c.name, 'value': c.value,
                               'path': c.path, 'expiry': c.expires})

        driver.get(examine_url)


def open_tab(driver, act):
    driver.execute_script(
        "window.open('about:blank', '{}');".format(act['id']))
    driver.switch_to.window(act['id'])
    driver.get(
        'https://{}/activity-try/answers?try_id={}'.format(act['backend'], act['id']))


def open_activities(driver, activities):
    max_tabs = int(settings.get('max_tabs', 100))
    activities = activities if len(activities) <= max_tabs else activities[:max_tabs]
    for activity in tqdm(activities):
        open_tab(driver, activity)
        time.sleep(0.5)


def login():
    # Retrieve the CSRF token first
    login_url = 'https://{backend}/site/login'.format(backend=teen_backend_list[0])
    rq = session.get(login_url)  # sets cookie
    soup = BeautifulSoup(rq.text, 'html.parser')
    csrftoken = soup.find(id='login-form').find(name='input').attrs['value']

    pswd = ask_pswd()

    login_data = {
        '_csrf': csrftoken,
        'LoginForm[username]': settings['username'],
        'LoginForm[password]': pswd,
    }

    resp = session.post(login_url, data=login_data, headers=dict(Referer=login_url))

    sp = BeautifulSoup(resp.text, "html.parser")

    try:
        login_str = sp.find('div', {"class": "authorization"}).text
        login_str = login_str.replace('Logout', '').strip()
        print(os.linesep + 'You are logged in as ' + login_str + os.linesep)
    except AttributeError:
        print('Wrong username or password')
        sys.exit()


def show_pending(pendings, is_army=False):
    if len(pendings) == 0:
        message = 'No pending activities for Army' if is_army else 'Congrats! No pending activities'
        print(os.linesep + message)
        return

    stats = OrderedDict()
    for pending in pendings:
        if pending['backend'] in stats:
            stats[pending['backend']].append(pending['activity_title'])
        else:
            stats[pending['backend']] = [pending['activity_title']]
    for key in stats:
        stats[key] = Counter(stats[key])

    message = 'Pending activities for Army' if is_army else 'Pending activities'
    print(os.linesep + message + os.linesep)
    for backend in stats:
        for activity in stats[backend]:
            print('{:4} {:25} {}'.format(stats[backend][activity], backend, activity))
