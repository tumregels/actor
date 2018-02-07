# -*- coding: utf-8 -*-

from actor import teen_backend_list, army_backend_list, teen_activity_list, army_activity_list, status, logger
from actor.__version__ import __logo__
from actor.browser import login, get_pending_activities, show_pending, start_browser, \
    login_backends, open_activities, get_all_activity_try_urls, get_army_activity_try_urls, add_date_filters
from actor.cli import cli
from actor.utils import sort_urls_by_activities

driver = None


def main():
    global driver  # use global driver to avoid selenium closing browser
    print(__logo__)
    login()

    teen_urls = get_all_activity_try_urls(teen_backend_list, teen_activity_list, status=status)
    army_urls = get_army_activity_try_urls(army_backend_list, army_activity_list, status=status)
    urls = sort_urls_by_activities(army_urls + teen_urls)
    urls = add_date_filters(urls)
    pending = get_pending_activities(urls)
    show_pending(pending)

    driver = start_browser()
    login_backends(driver, {activity['backend'] for activity in pending})
    # login_examine(driver)
    open_activities(driver, pending)


if __name__ == "__main__":
    try:
        # main()
        cli()
    except Exception as e:
        logger.exception(e)
        raise

