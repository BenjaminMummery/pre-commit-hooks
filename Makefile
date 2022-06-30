venv: venv/touchfile

venv/touchfile: test_requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur test_requirements.txt ; pip install -e .
	touch venv/touchfile

test: venv
	. venv/bin/activate; pytest --cov-report term-missing --cov=add_msg_issue_hook tests/

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
