# actor - activity opener

Application to open all activities from all backends at once.

## Setup Instructions for Mac OS X

1. clone the project from github and unzip `chromedriver.zip` inside `assets` folder

    `$ git clone https://github.com/tumregels/actor`

2. download and install [miniconda](https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
and [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=mac)

3. add your backend password to your `.bash_profile`

    `export BEPASS=yourpass`

4. create virtual environment named actor

    `$ conda create -n actor python=3.4`

5. open terminal and activate the virtual environment

    `$ source activate actor`
    
6. install dependencies

    `(actor) $ pip install -r requirements/dev.txt`

7. run `main.py` from terminal. At this point virtual environment named `actor` should be active

    `(actor) $ python main.py`
    
8. To generate binary you need to adjust `CONDA_HOME`, `ENV_DIR` variables inside `Makefile`.
Afterwards just run `$ make generate_actor_exe` which will create a binary named actor inside `release` folder.


