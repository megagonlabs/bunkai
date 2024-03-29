
GREP_EXCLUDE:=grep -v -e '\.eggs' -e '\.git' -e 'pyc$$' -e '\.idea' -e 'venv' -e 'python_env' -e 'egg-info' -e htmlcov -e 'work_scripts' -e mks -e node_modules


TARGET_DIRS:=./bunkai ./tests ./example \( -type d -name '.venv' -prune \) -or -type f

flake8:
	find $(TARGET_DIRS) | grep -v third | grep '\.py$$' | xargs flake8
black:
	find $(TARGET_DIRS) | grep -v third | grep '\.py$$' | xargs black --diff | diff /dev/null -
pyright:
	npx pyright
isort:
	find $(TARGET_DIRS) | grep -v third | grep '\.py$$' | xargs isort --diff | diff /dev/null -
pydocstyle:
	find $(TARGET_DIRS) | grep -v tests | xargs pydocstyle --ignore=D100,D101,D102,D103,D104,D105,D107,D203,D212

jsonlint:
	find .*json $(TARGET_DIRS) | grep '\.jsonl$$' | sort |xargs cat | python3 -c 'import sys,json; [json.loads(line) for line in sys.stdin]'
	find .*json $(TARGET_DIRS) | grep '\.json$$' | sort |xargs -n 1 -t python3 -m json.tool > /dev/null
	python3 -c "import sys,json;print(json.dumps(json.loads(sys.stdin.read()),indent=4,ensure_ascii=False,sort_keys=True))" < .markdownlint.json | diff -q - .markdownlint.json

yamllint:
	find . -name '*.yml' -type f | grep -v node_modules | xargs yamllint --no-warnings

check_version:
	python3 check_version.py --py bunkai/__init__.py --toml pyproject.toml



lint: flake8 black pyright isort yamllint pydocstyle check_version lint_cff

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

CC_REPORTER_VERSION:=latest
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

lint_markdown:
	find . -type d -o -type f -name '*.md' -print \
	| $(GREP_EXCLUDE) \
	| xargs npx markdownlint --config ./.markdownlint.json

lint_cff:
	cffconvert --validate
