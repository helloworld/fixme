black:
	black --fast --preview -l 88 fixme examples tests

ruff:
	ruff --fix .

check_ruff:
	ruff .

fix_all:
	make black
	make ruff

install_dev_python_modules_verbose:
	python scripts/install_dev_python_modules.py

install_dev_python_modules_with_examples_verbose:
	python scripts/install_dev_python_modules.py --install-examples

dev_install: install_dev_python_modules_verbose 

dev_install_with_examples: install_dev_python_modules_with_examples_verbose
