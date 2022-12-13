test_venv: test_venv/touchfile

test_venv/touchfile: test_requirements.txt
	test -d test_venv || virtualenv test_venv
	. test_venv/bin/activate; pip install -Ur test_requirements.txt ; pip install -e .
	touch test_venv/touchfile

test: test_venv
	. test_venv/bin/activate; pytest --cov-report term-missing --cov=add_msg_issue_hook --cov=strict_tdd_hook tests/

test_add_issue: test_venv
	. test_venv/bin/activate; pytest --cov-report term-missing --cov=add_msg_issue_hook tests/add_msg_issue_hook -x

test_tdd: test_venv
	. test_venv/bin/activate; pytest --cov-report term-missing --cov=strict_tdd_hook tests/strict_tdd_hook -x

precommit_test_tdd:
	pre-commit try-repo . strict-tdd

precommit_test_add_issue:
	pre-commit try-repo . add-msg-issue

clean:
	rm -rf test_venv
	find -iname "*.pyc" -delete
