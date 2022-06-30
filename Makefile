test_venv: test_venv/touchfile

test_venv/touchfile: test_requirements.txt
	test -d test_venv || virtualenv test_venv
	. test_venv/bin/activate; pip install -Ur test_requirements.txt ; pip install -e .
	touch test_venv/touchfile

test: test_venv
	. test_venv/bin/activate; pytest --cov-report term-missing --cov=add_msg_issue_hook tests/

clean:
	rm -rf test_venv
	find -iname "*.pyc" -delete