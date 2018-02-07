.PHONY: mkdir_release generate_actor_exe generate_actor_app

define PYVERSION
from actor.__version__ import __version__
print(__version__)
endef

VERSION = $(shell python -c '$(PYVERSION)')
MKDIR_P := mkdir -p

CONDA_HOME = $(HOME)/miniconda3
CONDA_BIN_DIR = $(CONDA_HOME)/bin

ENV_NAME = actor
ENV_DIR = $(CONDA_HOME)/envs/$(ENV_NAME)
ENV_BIN_DIR = $(ENV_DIR)/bin
ENV_LIB_DIR = $(ENV_DIR)/lib
ENV_PYTHON = $(ENV_BIN_DIR)/python
ENV_CONDA = $(ENV_BIN_DIR)/conda

default:
	@echo 'python command: $(ENV_PYTHON)'
	@echo 'conda command: $(ENV_CONDA)'

mkdir_release:
	@${MKDIR_P} ./release/dist/$(VERSION)

create_actor_env:
	$(CONDA_BIN_DIR)/conda create -n actor python=3.4

activate:
	source activate actor

deactivate:
	deactivate activate

show_zip_content:
	unzip -l ./release/dist/actor-beta.zip

echo_version:
	@echo $(VERSION)

generate_actor_exe: mkdir_release
	@$(ENV_BIN_DIR)/pyinstaller main.py --onefile --name actor  --clean \
	--distpath ./release/dist/$(VERSION)/actor.app/Contents/Resources --workpath ./release/build --specpath ./release

generate_actor_app: mkdir_release
	@$(ENV_BIN_DIR)/pyinstaller term.spec \
	--distpath ./release/dist/$(VERSION) --workpath ./release/build \
	--specpath . --noconfirm --clean; \
	\cp ./release/config.txt ./release/dist/$(VERSION)/actor.app/Contents/Resources/config.txt; \
	\cp -R ./assets ./release/dist/$(VERSION)/actor.app/Contents/Resources;
	$(MAKE) generate_actor_exe