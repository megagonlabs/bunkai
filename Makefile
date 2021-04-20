
all: lint lint_markdown test

include mks/lint.mk
include mks/lbd.mk
include mks/vanilla.mk


.PHONY: all setup \
	flake8 autopep8 mypy isort jsonlint yamllint\
	terms_check_path term_check_method term_check_file_content\
	check_firstline \
	lint \
	_run_isort _coverage\
	test test-coverage setup-cc test-cc\
	setup_node_module lint_markdown circleci_local

.DELETE_ON_ERROR:

circleci_local:
	circleci local execute
