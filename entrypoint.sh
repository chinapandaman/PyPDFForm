#!/bin/bash
set -e

find /pypdfform/scripts -type f -name "*.sh" -print0 | xargs -0 dos2unix -q
export PYPDFFORM_ENV=container

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

| Command  | Usage                                             | Documentation                                                                |
-----------------------------------------------------------------------------------------------------------------------------------------------
| coverage | Run all tests and generate HTML coverage reports. | https://chinapandaman.github.io/PyPDFForm/dev_test/#generate-coverage-report |
| docs     | Host the documentation site locally.              | https://chinapandaman.github.io/PyPDFForm/dev_doc/                           |
| linting  | Run all linters on the code.                      | N/A                                                                          |
| test     | Run all tests and enforce 100% coverage.          | https://chinapandaman.github.io/PyPDFForm/dev_test/                          |

EOF

exec "$@"
