# SETUP
test_venv: test_venv/touchfile

test_venv/touchfile: test_requirements.txt
	test -d test_venv || virtualenv test_venv
	. test_venv/bin/activate; \
	pip install -Ur test_requirements.txt ; \
	pip install -e .
	touch test_venv/touchfile

clean:
	rm -rf test_venv
	rm -f .coverage
	find . -name "*.pyc" -type f -delete
	find . -name "*__pycache__" -delete

# GENERAL TESTING
test: test_venv
	. test_venv/bin/activate; pytest \
	-m "not slow" \
	tests/

test_all: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/

# TESTING BY LEVEL
test_unit: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/*/test_unit_*.py -x

test_integration: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src/add_copyright_hook \
	--cov=src/add_msg_issue_hook \
	--cov=src/sort_file_contents_hook \
	tests/*/test_integration_*.py -x

test_system: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/*/test_system_*.py -x

# TESTING BY HOOK
test_shared: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src/_shared \
	tests/shared -x

test_add_issue: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src/add_msg_issue_hook \
	tests/add_msg_issue_hook -x

test_add_copyright: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src/add_copyright_hook \
	tests/add_copyright_hook -x

test_sort_file_contents: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src/sort_file_contents_hook \
	tests/sort_file_contents_hook -x

