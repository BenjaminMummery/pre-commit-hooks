.PHONY: all clean test

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

# INSTALL
install:
	uv sync
	uv run pre-commit install

# GENERAL TESTING
test: test_unit test_integration
	@uv run python -c "$$PRETTYPRINT_PYSCRIPT"

test_all: test_unit test_integration test_system
	@uv run python -c "$$PRETTYPRINT_PYSCRIPT"

# TESTING BY LEVEL
test_unit:
	@uv run python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING UNIT TESTS; \
	uv run pytest src/ -x

test_integration:
	@uv run python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING INTEGRATION TESTS; \
	uv run pytest tests/*/test_integration_*.py -x

test_system:
	@uv run python -c "$$PRETTYPRINT_PYSCRIPT" RUNNING SYSTEM TESTS; \
	uv run pytest tests/*/test_system_*.py -x

# RUNNING PRE-COMMIT HOOKS
lint:
	@SKIP=add-copyright uv run pre-commit run --all-files
