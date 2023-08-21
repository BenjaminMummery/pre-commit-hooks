# Copyright (c) 2023 Benjamin Mummery


class SetupCfgExample:
    def __init__(
        self,
        correctly_formatted: str,
        incorrectly_formatted: str,
        stdout: str,
    ):
        self.correctly_formatted: str = correctly_formatted
        self.incorrectly_formatted: str = incorrectly_formatted
        self.stdout: str = stdout


UnsortedEntries = SetupCfgExample(
    correctly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    gitpython >= 3.1.31
    identify >= 2.5.24
    pyyaml >= 5.4.1

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    testing*
    tests*

[bdist_wheel]
universal = True
""",
    incorrectly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    pyyaml >= 5.4.1
    gitpython >= 3.1.31
    identify >= 2.5.24

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    tests*
    testing*

[bdist_wheel]
universal = True
""",
    stdout="""[options]
install_requires =
\033[91m    pyyaml >= 5.4.1
    gitpython >= 3.1.31
    identify >= 2.5.24\033[0m
\033[92m    gitpython >= 3.1.31
    identify >= 2.5.24
    pyyaml >= 5.4.1\033[0m

[options.packages.find]
exclude =
\033[91m    tests*
    testing*\033[0m
\033[92m    testing*
    tests*\033[0m

""",
)

UnsortedEntriesWithInlineComments = SetupCfgExample(
    correctly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    gitpython >= 3.1.31  # Comment explaining why we need this one.
    identify >= 2.5.24
    pyyaml >= 5.4.1

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    testing*
    tests*

[bdist_wheel]
universal = True
""",
    incorrectly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    pyyaml >= 5.4.1
    gitpython >= 3.1.31  # Comment explaining why we need this one.
    identify >= 2.5.24

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    tests*
    testing*

[bdist_wheel]
universal = True
""",
    stdout="""[options]
install_requires =
\033[91m    pyyaml >= 5.4.1
    gitpython >= 3.1.31  # Comment explaining why we need this one.
    identify >= 2.5.24\033[0m
\033[92m    gitpython >= 3.1.31  # Comment explaining why we need this one.
    identify >= 2.5.24
    pyyaml >= 5.4.1\033[0m

[options.packages.find]
exclude =
\033[91m    tests*
    testing*\033[0m
\033[92m    testing*
    tests*\033[0m

""",
)


UnsortedEntriesWithCommentLines = SetupCfgExample(
    correctly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    gitpython >= 3.1.31
    # Comment explaining why we need this one.
    identify >= 2.5.24
    pyyaml >= 5.4.1

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    testing*
    tests*

[bdist_wheel]
universal = True
""",
    incorrectly_formatted="""[metadata]
name = pre_commit_hooks
version = 1.1.0
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/BenjaminMummery/pre-commit-hooks
author = Benjamin Mummery
author_email = benjamin.mummery@zapatacomputing.com
license = MIT
license_file = LICENSE
classifiers =
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy

[options]
packages = find:
python_requires = >=3.8
install_requires =
    pyyaml >= 5.4.1
    gitpython >= 3.1.31
    # Comment explaining why we need this one.
    identify >= 2.5.24

[options.entry_points]
console_scripts =
    add-copyright = src.add_copyright_hook.add_copyright:main
    add-msg-issue = src.add_msg_issue_hook.add_msg_issue:main
    format-setup-cfg = src.format_setup_cfg_hook.format_setup_cfg:main
    sort-file-contents = src.sort_file_contents_hook.sort_file_contents:main

[options.packages.find]
exclude =
    tests*
    testing*

[bdist_wheel]
universal = True
""",
    stdout="""[options]
install_requires =
\033[91m    pyyaml >= 5.4.1
    gitpython >= 3.1.31
    # Comment explaining why we need this one.
    identify >= 2.5.24\033[0m
\033[92m    gitpython >= 3.1.31
    # Comment explaining why we need this one.
    identify >= 2.5.24
    pyyaml >= 5.4.1\033[0m

[options.packages.find]
exclude =
\033[91m    tests*
    testing*\033[0m
\033[92m    testing*
    tests*\033[0m

""",
)
