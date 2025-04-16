#!/bin/bash
set -e

mkdir -p temp
git config --global --add safe.directory /pypdfform
find /pypdfform/scripts -type f -name "*.sh" -print0 | xargs -0 dos2unix -q
export PYPDFFORM_ENV=container

echo "alias clean='make clean-temp'" >> /root/.bashrc
echo "alias compare='(trap \"kill 0\" SIGINT; make serve-files > /dev/null 2>&1 & make compare-pdf-diffs && echo \"Finished comparing.\" & wait)'" >> /root/.bashrc
echo "alias coverage='make coverage-all'" >> /root/.bashrc
echo "alias docs='make serve-docs'" >> /root/.bashrc
echo "alias server='make serve-files'" >> /root/.bashrc
echo "alias linting='make linting'" >> /root/.bashrc
echo "alias test='make test-all'" >> /root/.bashrc
echo "alias update='make generate-new-pdf-samples'" >> /root/.bashrc

cat << "EOF"

 /$$$$$$$            /$$$$$$$  /$$$$$$$  /$$$$$$$$ /$$$$$$$$                               
| $$__  $$          | $$__  $$| $$__  $$| $$_____/| $$_____/                               
| $$  \ $$ /$$   /$$| $$  \ $$| $$  \ $$| $$      | $$     /$$$$$$   /$$$$$$  /$$$$$$/$$$$ 
| $$$$$$$/| $$  | $$| $$$$$$$/| $$  | $$| $$$$$   | $$$$$ /$$__  $$ /$$__  $$| $$_  $$_  $$
| $$____/ | $$  | $$| $$____/ | $$  | $$| $$__/   | $$__/| $$  \ $$| $$  \__/| $$ \ $$ \ $$
| $$      | $$  | $$| $$      | $$  | $$| $$      | $$   | $$  | $$| $$      | $$ | $$ | $$
| $$      |  $$$$$$$| $$      | $$$$$$$/| $$      | $$   |  $$$$$$/| $$      | $$ | $$ | $$
|__/       \____  $$|__/      |_______/ |__/      |__/    \______/ |__/      |__/ |__/ |__/
           /$$  | $$                                                                       
          |  $$$$$$/                                                                       
           \______/                                                                        

Welcome to the PyPDFForm development container!

| Command  | Usage                                                   | Documentation                                                                |
-----------------------------------------------------------------------------------------------------------------------------------------------------
| clean    | Remove any temporarily generated PDFs.                  | N/A                                                                          |
| compare  | Compare PDF samples before and after changing the code. | N/A                                                                          |
| coverage | Run all tests and generate HTML coverage reports.       | https://chinapandaman.github.io/PyPDFForm/dev_test/#generate-coverage-report |
| docs     | Host the documentation site locally.                    | https://chinapandaman.github.io/PyPDFForm/dev_doc/                           |
| server   | Start an HTTP file server from the root of the code.    | N/A                                                                          |
| linting  | Run all linters on the code.                            | N/A                                                                          |
| test     | Run all tests and enforce 100% coverage.                | https://chinapandaman.github.io/PyPDFForm/dev_test/                          |
| update   | Update PDF samples after changing the code              | N/A                                                                          |

EOF

exec "$@"
