#!/bin/bash
set -e

mkdir -p temp
git config --global --add safe.directory /pypdfform
find /pypdfform/scripts -type f -name "*.sh" -print0 | xargs -0 dos2unix -q
export PYPDFFORM_ENV=container

echo "PS1='\[\e[34m\]Enter \[\e[38;5;220m\]help\[\e[34m\] for commands > \[\e[0m\] '" >> ~/.bashrc
echo "alias help='cat ~/.container_docs.txt'" >> ~/.bashrc

echo "alias clean='make clean-temp'" >> ~/.bashrc
echo "alias compare='(trap \"kill 0\" SIGINT; make serve-files > /dev/null 2>&1 & make compare-pdf-diffs && echo \"Finished comparing.\" & wait)'" >> ~/.bashrc
echo "alias coverage='make coverage-all'" >> ~/.bashrc
echo "alias docs='make serve-docs'" >> ~/.bashrc
echo "alias format='make format-code'" >> ~/.bashrc
echo "alias server='make serve-files'" >> ~/.bashrc
echo "alias linting='make linting'" >> ~/.bashrc
echo "alias test='make test-all'" >> ~/.bashrc
echo "alias update='make generate-new-pdf-samples'" >> ~/.bashrc

cat << "EOF" > ~/.container_docs.txt

[38;5;220m /$$$$$$$            /$$$$$$$  /$$$$$$$  /$$$$$$$$[34m /$$$$$$$$                               [0m
[38;5;220m| $$__  $$          | $$__  $$| $$__  $$| $$_____/[34m| $$_____/                               [0m
[38;5;220m| $$  \ $$ /$$   /$$| $$  \ $$| $$  \ $$| $$      [34m| $$     /$$$$$$   /$$$$$$  /$$$$$$/$$$$ [0m
[38;5;220m| $$$$$$$/| $$  | $$| $$$$$$$/| $$  | $$| $$$$$   [34m| $$$$$ /$$__  $$ /$$__  $$| $$_  $$_  $$[0m
[38;5;220m| $$____/ | $$  | $$| $$____/ | $$  | $$| $$__/   [34m| $$__/| $$  \ $$| $$  \__/| $$ \ $$ \ $$[0m
[38;5;220m| $$      | $$  | $$| $$      | $$  | $$| $$      [34m| $$   | $$  | $$| $$      | $$ | $$ | $$[0m
[38;5;220m| $$      |  $$$$$$$| $$      | $$$$$$$/| $$      [34m| $$   |  $$$$$$/| $$      | $$ | $$ | $$[0m
[38;5;220m|__/       \____  $$|__/      |_______/ |__/      [34m|__/    \______/ |__/      |__/ |__/ |__/[0m
[38;5;220m           /$$  | $$                              [34m                                         [0m
[38;5;220m          |  $$$$$$/                              [34m                                         [0m
[38;5;220m           \______/                               [34m                                         [0m

Welcome to the PyPDFForm development container!

| Command  | Usage                                                   | Documentation                                                                       |
------------------------------------------------------------------------------------------------------------------------------------------------------------
| clean    | Remove any temporarily generated PDFs.                  | N/A                                                                                 |
| compare  | Compare PDF samples before and after changing the code. | N/A                                                                                 |
| coverage | Run all tests and generate HTML coverage reports.       | https://chinapandaman.github.io/PyPDFForm/latest/dev_test/#generate-coverage-report |
| docs     | Host the documentation site locally.                    | https://chinapandaman.github.io/PyPDFForm/latest/dev_doc/                           |
| format   | Format the code with black and isort.                   | N/A                                                                                 |
| server   | Start an HTTP file server from the root of the code.    | N/A                                                                                 |
| linting  | Run all linters on the code.                            | N/A                                                                                 |
| test     | Run all tests and enforce 100% coverage.                | https://chinapandaman.github.io/PyPDFForm/latest/dev_test/                          |
| update   | Update PDF samples after changing the code.             | N/A                                                                                 |

EOF

cat ~/.container_docs.txt

exec "$@"
