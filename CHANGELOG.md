# CHANGELOG



## v2.3.0 (2024-05-20)

### Feature

* feat: support html files for add/update copyright hooks. (#86)

* feat: support html files for add/update copyright hooks.

* style: sort language lists.

* test: set email as well as username in git workspaces. ([`be4b34d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/be4b34d79c9f955db343a62d8a2d6025ed7c6815))


## v2.2.0 (2024-05-17)

### Feature

* feat: support javascript. (#70) ([`dbe596c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/dbe596cdb8669d8a9fd122251d92f010c4cdada5))


## v2.1.0 (2024-04-18)

### Ci

* ci: automate release (#46) ([`82ae87f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/82ae87f5d51b22d291af5cb8456420864f13d686))

### Feature

* feat: support setup.cfg configuration (#60)

* refactor: abstract config reading.

* test: add test to cover abstraction of reading config.

* chore: remove outmoded test.

* test: add test for detecting setup.cfg config files.

* feat: detect setup.cfg files.

* feat: parse cgf config files.

* refactor: abstract config file name in fixture.

* test: test formatting characters in configs.

* test: add integration tests for setup.cfg parsing.

* test: add integration tests for setup.cfg parsing.

* docs: update README ([`fede94c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/fede94cbc7e502e64de03b20a1c2cccfa9f589aa))

### Unknown

* Refactor/reorganise tests (#45)

* refactor: move unit tests into src.

* test: import from file under test rather than modules.

* ci: exclude test files from coverage.

* test: add unit test for raising a NotARepoError when it&#39;s not a repo.

* feat: explicitely re-raise NotARepoError.

* test: add test for no existing commits.

* refactor: unify test fixtures.

* test: add test for _get_first_commit happy path.

* test: add test for argparsing.

* test: stop ignoring coverage uninitiated git repo error handling.

* test: test add shebang.

* test: add test for inserting copyright string into content.

* test: add tests for formatting and config reading.

* test: add tests for _ensure_copyright_string()

* test: add tests for Main

* docs: add explanation for config heirarchy.

* test: add unit tests for add_msg_issue_hook

* feat: strip newlines.

* test: add tests for _insert_issue_into_message.

* test: add tests for parse args.

* test: add tests for main

* test: add tests for sorting lines.

* test: add tests for separating leading comment.

* docs: update comment for clarity.

* test: add tests for identifying sections.

* test: add test for find duplicates.

* test: add tests for sorting contents.

* test: add tests for main

* refactor: use patch properly.

* docs: better comment explanations.

* test: add tests for update copyright.

* test: add integration test coverage for add copyright failure states.

* chore: remove empty test files.

* ci: report unit test coverage.

* ci: report unit coverage

* ci: limit fixture scope@

* ci: reporting unit coverage doesn&#39;t work, remove for now. ([`9d17a11`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/9d17a11152d83ab42b813fe22957ccf2a3ebe2f1))


## v2.0.0 (2023-10-30)

### Unknown

* Refactor/testing (#42)

* test: add integration tests for add_msg_issue.

* feat: block commit if add issue hook errors.

* test: add integration tests for sorting files.

* test: add tests for failure states.

* feat: fail for commented duplicates.

* test: add system tests for sorting file contents.

* test: update tests

* docs: update README

* test: add tests for shared utility failure states.

* refactor: correctly name unit tests.

* refactor: remove unused shared utilities.

* feat: remove rst checker hook.

* test: add unit tests for copyright parsing.

* refactor: better controls on single/multiuple line matching.

* test: full unit tests for copyright parsing.

* refactor: move parsing individual comment line to private.

* test: add tests for multiple copyright string failure state.

* test: unit tests for all shared classes.

* refactor: use files resolver in all aplicable hooks.

* test: cleaner exception testing.

* test: add 3.11 testing.

* feat: encapsulate toml implementation.

* chore: mark imli imports as uncovered ([`fed54b1`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/fed54b1ee8b7f4fb3b0eb5d6c03e03623e6f8418))

* Copyright V2 (#41)

* feat: excise previous hook

* test: add tests for null hypothesis for add copyright.

* feat: minimal add_copyright hook.

* test: add tests for adding copyright to empty files.

* test: add tests for adding copyright to files with content.

* feat: adding copyright to files.

* test: check stdout.

* feat: write file changes to stdout.

* test: add tests for reading the git username.

* feat: read git username.

* test: add system-level tests.

* test: add tests for handling shebangs.

* feat: handle shebangs.

* test: add test for custom name argument.

* feat: handle name args.

* refactor: fix year for testing.

* test: add tests for inferring copyright start year.

* feat: infer start date from git history.

* refactor: migrate setup.py to pyproject.toml

* refactor: migrate setup.cfg to pyproject.toml.

* refactor: migrate from requirements.txt to pyproject.toml.

* refactor: shared resolvers should be public.

* refactor: tests.

* feat: parse pyproject files.

* test: add test for different number of lines between shebang and content.

* refactor: migrate mypy and pytest config to pyproject.toml

* test: add tests for missing config file or section.

* feat: handle missing config files / sections.

* test: add test for reading name from config.

* feat: read name from config file.

* test: add test for erroring out when unsupported config options are supplied.

* feat: raise exception if unsupported config options are provided.

* test: add test checking that cli name args overrule config files.

* test: add test for custom lagnuage formatting in config.

* feat: handle custom formatting.

* feat: handle custom formatting.

* test: add tests for custom formatting.

* test: add tests for custom formatting copyright strings.

* feat: allow setting custom copyrigh comment format per-language.

* test: add tests for failure states.

* test: add tests for failure states.

* ci: nicer output from make.

* chore: update pre-commit config

* test: add system tests for failure cases.

* feat: explicit re-raise exceptions.

* test: add tests for existing multiple-year copyrights.

* docs: update readme.

* test: add tests for global config formats.

* feat: allow global format configuration.

* test: add tests for configuration.

* docs: update readme.md

* test: add test for update copyright hook null hypothesis.

* feat: null case for update-copyright hook.

* fixup! test: add test for update copyright hook null hypothesis.

* test: add tests for updating single-date copyright strings.

* docs: update docstring.

* test: add tests for updating single-date docstrings.

* feat: update copyright strings.

* docs: update docstring.

* test: add tests for updating multiple-date docstrings.

* test: add tests for populated files without copyright.

* docs: update readme.

* feat: remove old add_copyright.

* ci: remove reliance on test_requirements.

* test: adapt tests for ci paths.

* test: add tests for inverted start-end dates.

* test: more informative output on fail.

* test: adapt tests for ci. ([`8915d47`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/8915d4760ae626834da63a777e76e0f65b2f6570))


## v1.5.0 (2023-09-29)

### Feature

* feat: check date of first commit for a file and insert date range if different from current year (#25)

* chore: update pre-commit config.

* feat: Infer date range from file commits.

* test: test infer date range from commits.

* test: test infer date range from commits.

* docs: update README for removal of &#39;year&#39;

* docs: update docstring.

* chore: add env to gitignore.

* test: add tests for infer end year.

* refactor: clean up infer logic. ([`1dea06e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/1dea06ea2ae0c260c413bb7ab55201f1039728d5))

### Unknown

* 38 new hook check docstrings parse as rst (#39)

* test: basic test setup for new hook.

* feat: basic hook setup.

* test: add remaining null-hypothesis system tests.

* test: add null-hypothesis integration tests.

* feat: return int.

* test: add test for failing rst check.

* feat: fail for bad rst.

* chore: better makefile output.

* refactor: cleaner test construction.

* test: add tests for printing output.

* feat: print errors to stdout.

* fixup! test: add tests for printing output.

* ci: automate integration tests

* docs: update readme.

* ci: report integration coverage. ([`01489fa`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/01489fa20bebc92dd53e31092f78acb9cc452aae))

* Docs: fill out docstring fields (#34)

* refactor: pull out adding comment markers as a separate unit.

* feat: add language support framework.

* feat: c++ support.

* test: tests for comment marker matching.

* docs: update README.md

* test: ffs mypy

* test: remove mypy args.

* docs: fill out docstring fields. ([`1901790`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/190179085a842ef1847e81836e032b1712167d5f))

* 5 extend copyright chacking to additional languages (#33)

* refactor: pull out adding comment markers as a separate unit.

* feat: add language support framework.

* feat: c++ support.

* test: tests for comment marker matching.

* docs: update README.md

* test: ffs mypy

* test: remove mypy args. ([`d39bdde`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/d39bddeb9139fbe7e57345188fd21568338adffe))

* Benjamin mummery patch 1 (#32)

* Create python-app.yml

* Update and rename python-app.yml to tests.yml

* Update tests.yml

* test: avoid autospecing mocks.

[PATCH-1]

* test: improve auto testing.

[PATCH-1]

* chore: delete outdated file.

[PATCH-1]

* fix: python-versions

[PATCH-1]

* WIP: simplify unit tests action?

[PATCH-1]

* WIP

[PATCH-1]

* test: automated system tests.

[PATCH-1]

* fix: no whitespace in job names.

[PATCH-1]

* fix: add pre-commit to test requirements.

[PATCH-1]

* rename unit_tests

[PATCH-1]

* fix: ensure git username is always set.

[PATCH-1]

* test: add coverage action.

[PATCH-1]

* fix: remove term missing

[PATCH-1]

* feat: comment with coverage

[PATCH-1]

* test: black and mypy

[PATCH-1]

* fix: point mypyp to files

[PATCH-1]

* test: config mypy

[PATCH-1]

* test: mypy ini

[PATCH-1]

* test: mypy ini

[PATCH-1]

* test: mypy ini

[PATCH-1]

* fix: typing dependencies.

[PATCH-1]

* style: fix typing.

[PATCH-1]

* test: point action to mypy config.

[PATCH-1]

* test: mypy should be as strict in ci/cd as it is in git hooks.

[PATCH-1]

* test: mypy should be as strict in ci/cd as it is in git hooks.

[PATCH-1] ([`afbc3d6`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/afbc3d60384bda4c1f4b3030bfebbef65f5fbf7b))

* Create python-app.yml (#31)

* Create python-app.yml

* Update and rename python-app.yml to tests.yml

* Update tests.yml

* test: avoid autospecing mocks.

[PATCH-1]

* test: improve auto testing.

[PATCH-1]

* chore: delete outdated file.

[PATCH-1]

* fix: python-versions

[PATCH-1]

* WIP: simplify unit tests action?

[PATCH-1]

* WIP

[PATCH-1]

* test: automated system tests.

[PATCH-1]

* fix: no whitespace in job names.

[PATCH-1]

* fix: add pre-commit to test requirements.

[PATCH-1]

* rename unit_tests

[PATCH-1]

* fix: ensure git username is always set.

[PATCH-1] ([`a2d8110`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/a2d81107efaa6e09037b84f2d27833ac174151ef))


## v1.4.0 (2023-05-23)

### Unknown

* Release (#22)

* docs: update README

* docs: describ --unique flag

* docs: bump version in README

* refactor: mock everything not being tested for unit tests.

* test: streamline mocking and coverage.

* refactor: full mocking for unit tests

* WIP

* WIP

* test: tests for ParsedCopyrightString.

* test: add test for missing git username.

* chore: neat labels for test structure.

* docs: add code structure to msg_issue docstring.

* docs: add code structure to module docstrings.

* docs: add typehint.

* docs: add typehint.

* feat: ready for release. ([`3954a0f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/3954a0f4f8b1c9ee8c6ec422dca0d9bb22035d96))

* Feat/gitignore sectioned sorter ensure unique (#21)

* feat: add unique argument

* feat: remove duplicates if unique arg is set

* test: system-level test for uniqueness chacking. ([`297d1fa`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/297d1fa0d504df4dc3c664c2a5d79624a4fae6a0))

* 19 add copyright hook update date ranges in existing copyright comments (#20)

* chore: bump pre-commit config

* test: add system tests for updating year ranges.

* refactor: move hooks into src directory.

* test: add pre-commit system tests.

* test: add system tests for updating date ranges.

* fix: actually call read

* feat: make parsed string information available in _ensure_copyright_string

* feat: glue code for updating existing copyright strings.

* feat: update date reanges in existing copyright strings.

* Update .pre-commit-config.yaml

* chore: update .pre-commit config ([`18ef540`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/18ef5403dd5ab509d8c4accc3579928867c0961a))


## v1.3.0 (2023-03-08)

### Fix

* fix: remove unnecessary r-strings. ([`50b6f92`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/50b6f9231fb9baed39a441885329fe0c2187613e))

### Unknown

* Feat/gitignore sectioned sorter (#17)

* refactor: move file resolver into shared.

* refactor: move file resolver into shared.

* refactor: set up locations and automation for new hook.

* feat: add argparse for sort_gitignore

* refactor: rename sort_gitignore to sort_file_contents.

The convention of passing .gitignore as the file argument to a git hook results in some file containing the word gitignore in their names getting sorted as well. This changes avoids that while also reflecting the fact that the hook has utility beyond simply gitignore.

* refactor: rename sort_gitignore to sort_file_contents.

The convention of passing .gitignore as the file argument to a git hook results in some file containing the word gitignore in their names getting sorted as well. This changes avoids that while also reflecting the fact that the hook has utility beyond simply gitignore.

* feat: file reading

* feat: separate a list of strings into sections.

* fix: remove blank lines in early return.

* feat: separate leading comment from section.

* feat: line sorting.

* feat: functioning executable

* docs: update WIP docstring.

* feat: ignore comment characters when sorting. ([`5436c16`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5436c16cc4dcdaef4c164aeeb72f217151b9ac76))


## v1.2.5 (2023-03-06)

### Unknown

* Feat: allow date ranges (#16)

* feat: permit copyright date ranges

* docs: add explanation of regex strings ([`9bf241a`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/9bf241ae280bff3831623048892037f6a95d1ae5))


## v1.2.4 (2023-03-06)

### Chore

* chore: bump pre-commit repo version ([`3771f96`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/3771f963bee91d16656c4976f528a953e219fed1))

### Feature

* feat: widen copyright matching to allow any combination of &#39;copyright&#39;, &#39;(c)&#39; and/or &#39;©&#39; (#15) ([`64333b7`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/64333b7e9f7ac81805e5d464a40014ea87020994))


## v1.2.3 (2023-03-06)

### Chore

* chore: style, docstrings, copyright. (#14) ([`e69cb4f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/e69cb4ffe6e52c1a85dd68f610b699cde10e2e4d))

* chore: update external pre-commit hook versions ([`6834d5f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/6834d5f5bf2b35b7a275c36ca48d65a2272ee03f))


## v1.2.1 (2023-03-01)

### Documentation

* docs: update readme ([`9d1676d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/9d1676d5f5f31570f8c71189cc9fb069aa0a33f4))

### Unknown

* 11 refactor tests (#13)

* style: fix docstring formatting.

* test: remove duplicate tests and fill test coverage.

* style: clearer user-output. ([`fc2635d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/fc2635d2b85d1b94e7bf3d52fdff632eeab97e46))

* 11 refactor tests (#12)

* style: fix docstring formatting.

* test: remove duplicate tests and fill test coverage. ([`d7972f6`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/d7972f658daabb7b4cdcfcc6b43a3866c6bbf91c))

* 9 allow custom copyright string templates (#10)

* feat: add user-formatted copyright strings.

* test: add test for missing format field in config file. ([`a10b3f3`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/a10b3f366d15de52c11d3db2eac3802aeb115902))


## v1.1.1 (2023-02-20)

### Chore

* chore: add copyright strings. ([`6bb8720`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/6bb8720c737905d361fa0b85d53acfcf3bf8eff5))

### Unknown

* 6 allow external configuration of copyright info (#8)

* feat: allow read copyright info from config files.

* feat: allow partial config files.

* feat: allow partial configuration. ([`12c5a35`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/12c5a357269f6d83af6979f206c454946cb8c9c1))

* 4 add blank line after copyright string (#7)

* fix: ensure copyright string always followed by a blank line.

* test: update makefile.

* refactor: simplify makefile command. ([`5753b19`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5753b19525b73d9086d96656bfb04efa8497a394))


## v1.1.0 (2023-02-19)

### Chore

* chore: bump version no. ([`412863d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/412863d0f6062efb56330d7b16be76a874298c9c))

* chore: bump version (#3) ([`f40eb3f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/f40eb3ff93ddb3e9b75c305bf151a3ad91a58ee8))

* chore: bump pre-commit versions. ([`b8c48d6`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/b8c48d6915b3ad6956985421fe2c196dc4c09f74))

### Feature

* feat: refactor to support additional hooks ([`7c63121`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/7c63121a0fafc22170946fd82ed9a45e2ea31dc5))

* feat: bump pre-commit versions ([`627946c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/627946ca984d6af946a6de4d1f87054359163f73))

### Unknown

* Feat/add copyright hook (#2)

* feat: basic setup for new hook.

* fix: correct &#39;stage&#39; typo.

* chore: add .vscide to gitignore

* feat: parse file list

* chore: add egg-info to .gitignore.

* feat: extract git username

* docs: add docstringfor _get_git_user_name().

* feat: do not raise exception for unset git name

* feat: add copyright holder name argument

* feat: get current year.

* feat: raise ValueError if git username not set.

* docs: docstring for get current year

* feat: add resolvers.

* feat: add file resolver.

* feat: add _is_copyright_string method.

* docs: add docstring for _is_copyright_string.

* feat: search for copyright string in entire file rather than single line.

* feat: add ability to modify file contents.

* feat: modify files.

* test: add tests for glue code.

* refactor: use relative rather than absolute paths.

* feat: tell the user what files are changed.

* fix: remove unused format argument.

* test: add system tests.

* docs: update README for new add-copyright hook ([`99339b0`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/99339b0c2f8f82b70ad56f196d27ec0e3d4d18d2))


## v1.0.2 (2022-06-30)

### Chore

* chore: version bump ([`5d941ff`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5d941ffc65cb070a5231ec2c5f6af56e3cdc5b1f))

### Documentation

* docs: add vanilla hook instructions to README ([`b46cc3e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/b46cc3e666f1f643e4a6816e80640dba895ebf14))

### Fix

* fix: remove erronious print statement ([`5a23cad`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5a23cad6b1386115f59e24d978a63f6884102525))


## v1.0.1 (2022-06-30)

### Documentation

* docs: update README with more complete instructions ([`70dd4ed`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/70dd4ed2844ab96ea0aa94c8103179acd7efaaf0))

### Fix

* fix: rename test_venv to avoid clashing with preexisting venvs ([`1937506`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/19375069e42eb1847c0ee7c148ee7f10f94dbf66))

### Refactor

* refactor: simplify main and add a lot more comments ([`44ee344`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/44ee344c85cfc43b45f2447c461f89de0a2c636e))

### Test

* test: add makefile for easy testing ([`d6a5382`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/d6a53828fe678dc3625cd9d156aa93fc7f5f7cd4))

* test: Add system and integration tests ([`de49d3e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/de49d3e41f78993a404575e68e75b1e5381547ea))

* test: unit tests for add_msg_issue.py ([`0e5c9c5`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/0e5c9c5d3eefe26977591c0499cef692cef54e8c))

### Unknown

* Merge branch &#39;dev/tests&#39; ([`b1b51ea`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/b1b51ea7c3134651404cde19a828b361ceafb1b9))

* Improve error message (#1) ([`7f0361e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/7f0361e19fc2b2424c31d849226930be487928b1))


## v1.0.0 (2022-06-28)

### Breaking

* feat!: final prep before release ([`9385407`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/93854075c19cf63a9f0573c1f04f4d3bbd321aaa))


## v0.1.1 (2022-06-28)

### Ci

* ci: add pre-commit config for consistent contributing ([`955ee96`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/955ee96aec1ccebfd00f82c01b2aa76dc56d7165))

### Test

* test: more complete tests for add_msg_issue ([`0fb44c3`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/0fb44c3a59b45aa9551364a3817a2f9127844868))


## v0.1.0 (2022-06-28)

### Documentation

* docs: update README ([`4c37254`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/4c37254a1a4362c3c63f19f434cfb7d5d7b7b325))

### Unknown

* update version number ([`69e3398`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/69e3398e4c7b5597452a2b1ceb8335fea12dc3ab))

* initial commit ([`f8c8051`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/f8c80511cd083132a3f2f4669e6ac4ac854fa985))