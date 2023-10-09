.PHONY : test_unit test_system test_integration

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

test_all: test_venv test_unit test_integration test_system

# TESTING BY LEVEL
test_unit: test_venv
	@echo "===== RUNNING UNIT TESTS ====="
	@. test_venv/bin/activate; pytest \
	--cov=src \
	tests/*/test_unit_*.py -x

test_integration: test_venv
	@echo "===== RUNNING INTEGRATION TESTS ====="
	@. test_venv/bin/activate; pytest \
	--cov=src \
	tests/*/test_integration_*.py -x

test_system: test_venv
	@echo "===== RUNNING SYSTEM TESTS ====="
	@. test_venv/bin/activate; pytest \
	tests/*/test_system_*.py -x

# TESTING BY HOOK
test_shared: test_venv
	. test_venv/bin/activate; pytest \
	tests/shared -x

test_add_issue: test_venv
	. test_venv/bin/activate; pytest \
	tests/add_msg_issue_hook -x

test_add_copyright: test_venv
	. test_venv/bin/activate; pytest \
	tests/add_copyright_hook -x

test_sort_file_contents: test_venv
	. test_venv/bin/activate; pytest \
	tests/sort_file_contents_hook -x

test_check_docstrings_parse_as_rst: test_venv
	. test_venv/bin/activate; pytest \
	tests/check_docstrings_parse_as_rst_hook -x
