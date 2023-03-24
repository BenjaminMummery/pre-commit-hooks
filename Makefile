test_venv: test_venv/touchfile

test_venv/touchfile: test_requirements.txt
	test -d test_venv || virtualenv test_venv
	. test_venv/bin/activate; \
	pip install -Ur test_requirements.txt ; \
	pip install -e .
	touch test_venv/touchfile

make test_wip: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/ \
	-x

test_all: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/

test_unit: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/*/unit/ -x

test_integration: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/*/integration/ -x

test_system: test_venv
	. test_venv/bin/activate; pytest \
	--cov-report term-missing \
	--cov=src \
	tests/*/system/ -x

test: test_venv
	. test_venv/bin/activate; pytest \
	-m "not slow" \
	--cov-report term-missing \
	--cov=src \
	tests/

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


clean:
	rm -rf test_venv
	rm -f .coverage
	find . -name "*.pyc" -type f -delete
	find . -name "*__pycache__" -delete
