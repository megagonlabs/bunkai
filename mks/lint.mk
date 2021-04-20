
GREP_EXCLUDE:=grep -v -e '\.eggs' -e '\.git' -e 'pyc$$' -e '\.mypy' -e '\.idea' -e '\./venv' -e 'python_env' -e 'egg-info' -e htmlcov -e 'work_scripts' -e mks
TERMS_CHECK_CMD:=grep -e split -e divide
TERMS_CHECK_CONTENT_OPTION:=-e 文分割 -e 'coding: utf'

POETRY_NO_ROOT:= --no-root

dev_setup:
	poetry install $(POETRY_NO_ROOT) $(POETRY_OPTION)

setup:
	poetry install $(POETRY_OPTION)

TARGET_DIRS:=./bunkai ./tests ./example

flake8:
	find $(TARGET_DIRS) *.py | grep -v third | grep '\.py$$' | xargs flake8
autopep8:
	find $(TARGET_DIRS) *.py | grep -v third | grep '\.py$$' | xargs autopep8 -d | diff /dev/null -
mypy:
	find $(TARGET_DIRS) *.py | grep -v third | grep '\.py$$' | xargs mypy --python-version 3.7 --check-untyped-defs --strict-equality --no-implicit-optional
isort:
	find $(TARGET_DIRS) *.py | grep -v third | grep '\.py$$' | xargs isort --diff | diff /dev/null -
pydocstyle:
	pydocstyle $(TARGET_DIRS) --ignore=D100,D101,D102,D103,D104,D105,D107,D203,D212

jsonlint:
	find .*json $(TARGET_DIRS) -type f | grep -v 'mypy_cache' | grep '\.jsonl$$' | sort |xargs cat | python3 -c 'import sys,json; [json.loads(line) for line in sys.stdin]'
	find .*json $(TARGET_DIRS) -type f | grep -v 'mypy_cache' | grep '\.json$$' | sort |xargs -n 1 -t python3 -m json.tool > /dev/null
	find .*json $(TARGET_DIRS) -type f | grep -v 'mypy_cache' | grep '\.json$$' | sort |xargs -n 1 -t jsonlint
	python3 -c "import sys,json;print(json.dumps(json.loads(sys.stdin.read()),indent=4,ensure_ascii=False,sort_keys=True))" < .markdownlint.json | diff -q - .markdownlint.json

yamllint:
	find . -name '*.yml' -type f | xargs yamllint --no-warnings

terms_check_path:
	# check some words are not included in file name
	find . | $(GREP_EXCLUDE) | $(TERMS_CHECK_CMD); if [ $$? -eq 1 ]; then echo "pass term check"; else exit 1; fi

term_check_method:
	# check if some terms are wrote in python method names
	find . -type f | grep -v -e 'git' -e 'idea' -e 'mypy' -e 'python_env' | grep -e 'py$$' | xargs -L 1 python3 .circleci/show_method_names.py

term_check_file_content:
	# check if 文分割 is written somewhere in a file.
	find . -type f | $(GREP_EXCLUDE) | grep -v -e 'Makefile' -e 'show_method_names.py' -e 'example.py' | xargs grep $(TERMS_CHECK_CONTENT_OPTION); last_var=$$? ; if [ $${last_var} -eq 1 ] || [ $${last_var} -eq 123 ]; then echo "pass file content"; else exit 1; fi

check_firstline:
	find . -type f | grep -v -e 'git' -e 'idea' -e 'mypy' -e 'python_env' | grep -e 'py$$' | grep -v '__init__' | grep -v third | xargs python3 .circleci/check_head.py


lint: flake8 autopep8 mypy isort yamllint terms_check_path term_check_method term_check_file_content check_firstline pydocstyle

_run_isort:
	isort -rc .

_coverage:
	ulimit -n 1000 && coverage run -m unittest discover tests

GOLD_SAMPLE:=tests/sample.gold.txt
check_sample:
	sed "s/│//g" $(GOLD_SAMPLE) | poetry run bunkai | diff $(GOLD_SAMPLE) -


test: _coverage check_sample

test-coverage: test
	coverage report && coverage html

CC_REPORTER_VERSION:=0.6.3
setup-cc:
	mkdir -p ~/.local/bin-cc
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-$(CC_REPORTER_VERSION)-linux-amd64 > ~/.local/bin-cc/cc-test-reporter
	chmod +x ~/.local/bin-cc/cc-test-reporter
	~/.local/bin-cc/cc-test-reporter before-build

test-cc: test
	coverage xml && \
	 ~/.local/bin-cc/cc-test-reporter after-build\
	 --coverage-input-type coverage.py\
	 --exit-code $$?

setup_node_module:
	npm install markdownlint-cli

lint_markdown:
	find . -type d -o -type f -name '*.md' -print \
	| grep -v node_modules \
	| xargs npx markdownlint --config ./.markdownlint.json


