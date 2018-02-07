from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token

from actor import teen_backend_list, army_backend_list, teen_activity_list, army_activity_list, status
from actor.__version__ import __logo__
from actor.browser import login, get_pending_activities, show_pending, start_browser, \
    login_backends, open_activities, get_all_activity_try_urls, get_army_activity_try_urls, add_date_filters
from actor.utils import sort_urls_by_activities


def cli():
    global driver  # use global driver to avoid selenium closing browser
    print(__logo__)
    login()

    options = [
        'open all activities',
        'open army activities only',
        'show statistics only'
    ]

    option_completer = WordCompleter(
        words=options,
        ignore_case=True)

    while True:
        action = prompt(os.linesep + 'Enter action: ',
                        completer=option_completer,
                        get_bottom_toolbar_tokens=lambda cli: [(Token.Toolbar,
                                                                'Press repeatedly TAB key to choose from the list of options')],
                        style=style_from_dict({Token.Toolbar: '#ffffff bg:#333333'}),
                        display_completions_in_columns=True)

        if options[0] in action:
            teen_urls = get_all_activity_try_urls(teen_backend_list, teen_activity_list, status=status)
            army_urls = get_army_activity_try_urls(army_backend_list, army_activity_list, status=status)

            urls = sort_urls_by_activities(army_urls + teen_urls)
            urls = add_date_filters(urls)

            pending = get_pending_activities(urls)
            show_pending(pending)

            driver = start_browser()
            login_backends(driver, {activity['backend'] for activity in pending})
            open_activities(driver, pending)

        elif options[1] in action:
            army_urls = get_army_activity_try_urls(army_backend_list, army_activity_list, status=status)
            army_urls = add_date_filters(army_urls)

            pending = get_pending_activities(army_urls)
            show_pending(pending, is_army=True)

            driver = start_browser()
            login_backends(driver, {activity['backend'] for activity in pending})
            open_activities(driver, pending)

        elif options[2] in action:
            teen_urls = get_all_activity_try_urls(teen_backend_list, teen_activity_list, status=status)
            army_urls = get_army_activity_try_urls(army_backend_list, army_activity_list, status=status)

            pending_teen = get_pending_activities(teen_urls)
            pending_army = get_pending_activities(army_urls)

            show_pending(pending_teen)
            show_pending(pending_army, is_army=True)

        else:
            print('Wrong input value. Try again.')