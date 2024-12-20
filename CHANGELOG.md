# CHANGELOG


## v2.6.2 (2024-12-20)

### Bug Fixes

- Default to flake8-friendly copyright notices.
  ([#101](https://github.com/BenjaminMummery/pre-commit-hooks/pull/101),
  [`e4dfe10`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/e4dfe10f485fcead0cd11059a94c7a835f60caa0))

Co-authored-by: Benjamin Mummery <bmummery@psiquantum.com>


## v2.6.1 (2024-12-16)

### Bug Fixes

- Handle module level docstrings containing copyright markers.
  ([#100](https://github.com/BenjaminMummery/pre-commit-hooks/pull/100),
  [`4db3e5e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/4db3e5e4f7b02f280fb0536a4caa98e3a34425b0))

* chore: pass for spelling and clarity.

* test: add test for docstring copyright parsing.

* fix: handle incomplete comment markers in docstrings.

---------

Co-authored-by: Benjamin Mummery <bmummery@psiquantum.com>


## v2.6.0 (2024-12-16)

### Continuous Integration

- Add pull request template. ([#98](https://github.com/BenjaminMummery/pre-commit-hooks/pull/98),
  [`fa8e513`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/fa8e5139ca337c495702c040f2e0781c96cb9e8d))

* ci: add pull request template.

* ci: specify that semantics are case sensitive.

### Features

- Support copyright headers ([#99](https://github.com/BenjaminMummery/pre-commit-hooks/pull/99),
  [`c773cb7`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/c773cb74fd6c55e4440069a8265906407ea44cc2))

* test: add test for simple docstring copyrights.

* feat: add simple docstring copyrights.

* test: add tests for skipping files that already have copyright docstrings.

* feat: skip files with copyright in docstring.

* test: add test for adding copyright to existing docstring.

* feat: add copyright to existing docstrings if present.

* test: add tests for updating docstring copyrights.

* feat: update docstring copyrights.

* ci: only worry about unit tests for shared files.

* docs: update README for new docstr feature.

---------

Co-authored-by: Benjamin Mummery <bmummery@psiquantum.com>


## v2.5.0 (2024-09-23)

### Features

- Fully test no-test-imports.
  ([`5e2391f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5e2391fe02d8dd08bbc01f7a87151d6f59497b4f))

feat: fully test no-test-imports.

### Testing

- Fully test no-test-imports. ([#96](https://github.com/BenjaminMummery/pre-commit-hooks/pull/96),
  [`07f90ca`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/07f90ca20578ff40e4740a314a99e9a3238272e7))


## v2.4.0 (2024-06-21)

### Features

- Search top directory only. ([#93](https://github.com/BenjaminMummery/pre-commit-hooks/pull/93),
  [`ebd0ab2`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/ebd0ab269582b6d0eece7e4193561edc7700c42f))


## v2.3.2 (2024-05-21)

### Bug Fixes

- When erroring out due to multiple configs, report the found configs.
  ([#90](https://github.com/BenjaminMummery/pre-commit-hooks/pull/90),
  [`f371632`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/f3716321ffce45fc45863c0de25c007769160697))


## v2.3.1 (2024-05-21)

### Bug Fixes

- Don't error out in detached head mode.
  ([#89](https://github.com/BenjaminMummery/pre-commit-hooks/pull/89),
  [`e577435`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/e57743587ea9d925a1ca81e9a3c9dded4698ac49))


## v2.3.0 (2024-05-20)

### Features

- Support html files for add/update copyright hooks.
  ([#86](https://github.com/BenjaminMummery/pre-commit-hooks/pull/86),
  [`be4b34d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/be4b34d79c9f955db343a62d8a2d6025ed7c6815))

* feat: support html files for add/update copyright hooks.

* style: sort language lists.

* test: set email as well as username in git workspaces.


## v2.2.0 (2024-05-17)

### Features

- Support javascript. ([#70](https://github.com/BenjaminMummery/pre-commit-hooks/pull/70),
  [`dbe596c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/dbe596cdb8669d8a9fd122251d92f010c4cdada5))


## v2.1.0 (2024-04-18)

### Continuous Integration

- Automate release ([#46](https://github.com/BenjaminMummery/pre-commit-hooks/pull/46),
  [`82ae87f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/82ae87f5d51b22d291af5cb8456420864f13d686))

### Features

- Support setup.cfg configuration
  ([#60](https://github.com/BenjaminMummery/pre-commit-hooks/pull/60),
  [`fede94c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/fede94cbc7e502e64de03b20a1c2cccfa9f589aa))

* refactor: abstract config reading.

* test: add test to cover abstraction of reading config.

* chore: remove outmoded test.

* test: add test for detecting setup.cfg config files.

* feat: detect setup.cfg files.

* feat: parse cgf config files.

* refactor: abstract config file name in fixture.

* test: test formatting characters in configs.

* test: add integration tests for setup.cfg parsing.

* docs: update README


## v2.0.0 (2023-10-30)


## v1.5.0 (2023-09-29)

### Features

- Check date of first commit for a file and insert date range if different from current year
  ([#25](https://github.com/BenjaminMummery/pre-commit-hooks/pull/25),
  [`1dea06e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/1dea06ea2ae0c260c413bb7ab55201f1039728d5))

* chore: update pre-commit config.

* feat: Infer date range from file commits.

* test: test infer date range from commits.

* docs: update README for removal of 'year'

* docs: update docstring.

* chore: add env to gitignore.

* test: add tests for infer end year.

* refactor: clean up infer logic.


## v1.4.0 (2023-05-23)


## v1.3.0 (2023-03-08)

### Bug Fixes

- Remove unnecessary r-strings.
  ([`50b6f92`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/50b6f9231fb9baed39a441885329fe0c2187613e))


## v1.2.5 (2023-03-06)


## v1.2.4 (2023-03-06)

### Chores

- Bump pre-commit repo version
  ([`3771f96`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/3771f963bee91d16656c4976f528a953e219fed1))

### Features

- Widen copyright matching to allow any combination of 'copyright', '(c)' and/or '©'
  ([#15](https://github.com/BenjaminMummery/pre-commit-hooks/pull/15),
  [`64333b7`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/64333b7e9f7ac81805e5d464a40014ea87020994))


## v1.2.3 (2023-03-06)

### Chores

- Style, docstrings, copyright. ([#14](https://github.com/BenjaminMummery/pre-commit-hooks/pull/14),
  [`e69cb4f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/e69cb4ffe6e52c1a85dd68f610b699cde10e2e4d))

- Update external pre-commit hook versions
  ([`6834d5f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/6834d5f5bf2b35b7a275c36ca48d65a2272ee03f))


## v1.2.1 (2023-03-01)

### Documentation

- Update readme
  ([`9d1676d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/9d1676d5f5f31570f8c71189cc9fb069aa0a33f4))


## v1.1.1 (2023-02-20)

### Chores

- Add copyright strings.
  ([`6bb8720`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/6bb8720c737905d361fa0b85d53acfcf3bf8eff5))


## v1.1.0 (2023-02-19)

### Chores

- Bump pre-commit versions.
  ([`b8c48d6`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/b8c48d6915b3ad6956985421fe2c196dc4c09f74))

- Bump version ([#3](https://github.com/BenjaminMummery/pre-commit-hooks/pull/3),
  [`f40eb3f`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/f40eb3ff93ddb3e9b75c305bf151a3ad91a58ee8))

- Bump version no.
  ([`412863d`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/412863d0f6062efb56330d7b16be76a874298c9c))

### Features

- Bump pre-commit versions
  ([`627946c`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/627946ca984d6af946a6de4d1f87054359163f73))

- Refactor to support additional hooks
  ([`7c63121`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/7c63121a0fafc22170946fd82ed9a45e2ea31dc5))


## v1.0.2 (2022-06-30)

### Bug Fixes

- Remove erronious print statement
  ([`5a23cad`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5a23cad6b1386115f59e24d978a63f6884102525))

### Chores

- Version bump
  ([`5d941ff`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/5d941ffc65cb070a5231ec2c5f6af56e3cdc5b1f))

### Documentation

- Add vanilla hook instructions to README
  ([`b46cc3e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/b46cc3e666f1f643e4a6816e80640dba895ebf14))


## v1.0.1 (2022-06-30)

### Bug Fixes

- Rename test_venv to avoid clashing with preexisting venvs
  ([`1937506`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/19375069e42eb1847c0ee7c148ee7f10f94dbf66))

### Documentation

- Update README with more complete instructions
  ([`70dd4ed`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/70dd4ed2844ab96ea0aa94c8103179acd7efaaf0))

### Refactoring

- Simplify main and add a lot more comments
  ([`44ee344`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/44ee344c85cfc43b45f2447c461f89de0a2c636e))

### Testing

- Add makefile for easy testing
  ([`d6a5382`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/d6a53828fe678dc3625cd9d156aa93fc7f5f7cd4))

- Add system and integration tests
  ([`de49d3e`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/de49d3e41f78993a404575e68e75b1e5381547ea))

- Unit tests for add_msg_issue.py
  ([`0e5c9c5`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/0e5c9c5d3eefe26977591c0499cef692cef54e8c))


## v1.0.0 (2022-06-28)

### Features

- Final prep before release
  ([`9385407`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/93854075c19cf63a9f0573c1f04f4d3bbd321aaa))


## v0.1.1 (2022-06-28)

### Continuous Integration

- Add pre-commit config for consistent contributing
  ([`955ee96`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/955ee96aec1ccebfd00f82c01b2aa76dc56d7165))

### Testing

- More complete tests for add_msg_issue
  ([`0fb44c3`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/0fb44c3a59b45aa9551364a3817a2f9127844868))


## v0.1.0 (2022-06-28)

### Documentation

- Update README
  ([`4c37254`](https://github.com/BenjaminMummery/pre-commit-hooks/commit/4c37254a1a4362c3c63f19f434cfb7d5d7b7b325))
