.PHONY : test_unit test_system test_integration

define PRETTYPRINT_PYSCRIPT
import sys, os
if len(sys.argv) == 1:
	print("="*os.get_terminal_size().columns + "\n\n")
	exit()
else:
    text = " " + " ".join(sys.argv[1:]) + " "
full_width = os.get_terminal_size().columns
padwidth = int((full_width-len(text)-2)/2)
outstr = "\n" + "="*int(padwidth) + text + "="*int(padwidth)
while len(outstr) < full_width:
    outstr += "="
print(outstr)
endef
export PRETTYPRINT_PYSCRIPT

# SETUP
test_venv: test_venv/touchfile

test_venv/touchfile:
	test -d test_venv || virtualenv test_venv
	. test_venv/bin/activate; \
	pip install -e '.[dev]'
	touch test_venv/touchfile

clean:
	rm -rf test_venv
	rm -f .coverage
	find . -name "*.pyc" -type f -delete
	find . -name "*__pycache__" -delete

# GENERAL TESTING
test: test_venv test_unit test_integration
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT"

test_all: test_venv test_unit test_integration test_system
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT"

# TESTING BY LEVEL
test_unit: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING UNIT TESTS; \
	pytest --cov=src src/*/test_*.py -x

test_integration: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING INTEGRATION TESTS; \
	pytest --cov=src tests/*/test_integration_*.py -x

test_system: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING SYSTEM TESTS; \
	pytest tests/*/test_system_*.py -x


# TESTING BY HOOK
test_shared: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'SHARED' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	pytest src/_shared/test_* -x


test_add_issue: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'ADD_ISSUE' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/add_msg_issue_hook -x --cov=src/add_msg_issue_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	echo Nothing found

test_add_copyright: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'ADD_COPYRIGHT' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/add_copyright_hook -x --cov=src/add_copyright_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	pytest tests/add_copyright_hook/test_system_* -x

test_update_copyright: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'UPDATE_COPYRIGHT' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/update_copyright_hook -x --cov=src/update_copyright_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	pytest tests/update_copyright_hook/test_system_* -x

test_sort_file_contents: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'SORT_FILE_CONTENTS' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/sort_file_contents_hook/test_integration_* -x --cov=src/sort_file_contents_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	pytest tests/sort_file_contents_hook/test_system_* -x

test_no_testtools: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'NO_TESTTOOLS' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/no_import_testtools_in_src_hook/test_integration_* -x --cov=src/no_import_testtools_in_src_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	pytest tests/no_import_testtools_in_src_hook/test_system_* -x

test_americanise: test_venv
	@. test_venv/bin/activate; \
	python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING 'AMERICANISE' TESTS; \
	python -c "$$PRETTYPRINT_PYSCRIPT" UNIT TESTS; \
	echo Nothing found; \
	python -c "$$PRETTYPRINT_PYSCRIPT" INTEGRATION TESTS; \
	pytest tests/americanise_hook/test_integration_* -x --cov=src/americanise_hook; \
	python -c "$$PRETTYPRINT_PYSCRIPT" SYSTEM TESTS; \
	pytest tests/americanise_hook/test_system_* -x
