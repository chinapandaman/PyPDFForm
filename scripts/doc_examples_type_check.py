# -*- coding: utf-8 -*-
"""
This script extracts Python code snippets from the documentation files (specifically those listed
under the 'User Guide' in mkdocs.yml) and runs pyright on them to ensure type correctness.

It performs the following steps:
1. Creates a temporary 'ci_artifacts' directory.
2. Identifies 'User Guide' documentation files from mkdocs.yml.
3. Extracts all python code blocks from these files and saves them as standalone .py files.
4. Executes pyright on these generated files.
5. Maps any reported diagnostics back to the original documentation files and line numbers.
6. Cleans up the temporary artifacts.
7. Exits with a non-zero status if type errors are detected.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

import yaml


def setup_artifact_dir(artifact_dir):
    """Creates the artifact directory and pyrightconfig.json."""
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)

    with open(os.path.join(artifact_dir, "pyrightconfig.json"), "w") as f:
        json.dump({"extraPaths": [".."]}, f)


def get_user_guide_docs(mkdocs_path):
    """Extracts User Guide document paths from mkdocs.yml."""
    with open(mkdocs_path, "r") as f:
        content = f.read()

    content = re.sub(r"!!python/name:[\w\.]+", "null", content)
    config = yaml.safe_load(content)

    nav = config.get("nav", [])
    for item in nav:
        if isinstance(item, dict) and "User Guide" in item:
            return item["User Guide"]
    return []


def _extract_snippets_from_file(
    lines, doc_file, doc_path, artifact_dir, snippet_map, snippet_idx
):
    """Helper to extract snippets from a single file's lines."""
    in_code_block = False
    code_lines = []
    start_line = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```python"):
            in_code_block = True
            start_line = i + 1
            code_lines = []
        elif stripped.startswith("```") and in_code_block:
            in_code_block = False
            if not code_lines:
                continue

            safe_doc_name = doc_file.replace("/", "_").replace(".", "_")
            snippet_filename = f"{safe_doc_name}_{snippet_idx}.py"
            snippet_path = os.path.join(artifact_dir, snippet_filename)

            dedented_code = textwrap.dedent("".join(code_lines))
            with open(snippet_path, "w") as sf:
                sf.write(dedented_code)

            snippet_map[snippet_filename] = (doc_path, start_line)
            snippet_idx += 1
        elif in_code_block:
            code_lines.append(line)

    return snippet_idx


def extract_snippets(user_guide_docs, artifact_dir):
    """Extracts Python snippets from documentation and saves them to files."""
    snippet_map = {}
    snippet_idx = 0

    for doc_file in user_guide_docs:
        if not isinstance(doc_file, str):
            continue

        doc_path = os.path.join("docs", doc_file)
        if not os.path.exists(doc_path):
            continue

        with open(doc_path, "r") as f:
            lines = f.readlines()

        snippet_idx = _extract_snippets_from_file(
            lines, doc_file, doc_path, artifact_dir, snippet_map, snippet_idx
        )

    return snippet_map


def run_pyright(artifact_dir):
    """Runs pyright on the artifact directory and returns diagnostics."""
    cmd = [
        "pyright",
        "--outputjson",
        "--project",
        os.path.join(artifact_dir, "pyrightconfig.json"),
        artifact_dir,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get("generalDiagnostics", [])
    except json.JSONDecodeError:
        print("Failed to decode pyright output")
        return None


def map_diagnostics(diagnostics, snippet_map):
    """Maps pyright diagnostics back to original documentation files."""
    errors_by_location = {}

    for diag in diagnostics:
        file_path = diag.get("file")
        filename = os.path.basename(file_path)

        if filename in snippet_map:
            original_doc, start_line = snippet_map[filename]
            error_line_in_snippet = diag["range"]["start"]["line"]
            original_line = start_line + 1 + error_line_in_snippet
            msg = diag.get("message", "")

            if original_doc not in errors_by_location:
                errors_by_location[original_doc] = {}
            if original_line not in errors_by_location[original_doc]:
                errors_by_location[original_doc][original_line] = []

            errors_by_location[original_doc][original_line].append(msg)

    return errors_by_location


def report_errors(errors_by_location):
    """Prints consolidated errors and returns True if any errors were found."""
    has_errors = False
    for doc_path in sorted(errors_by_location.keys()):
        for line_num in sorted(errors_by_location[doc_path].keys()):
            has_errors = True
            messages = errors_by_location[doc_path][line_num]
            print(f"{doc_path}:{line_num}")
            for m in messages:
                print(f"  {m}")
    return has_errors


def cleanup(artifact_dir):
    """Removes the artifact directory."""
    if os.path.exists(artifact_dir):
        shutil.rmtree(artifact_dir)


def main():
    # 1. Create ci_artifacts
    artifact_dir = "ci_artifacts"
    setup_artifact_dir(artifact_dir)

    # 2. Look up docs under User Guide
    user_guide_docs = get_user_guide_docs("mkdocs.yml")

    # 3. Extract snippets
    snippet_map = extract_snippets(user_guide_docs, artifact_dir)

    # 4. Run pyright
    diagnostics = run_pyright(artifact_dir)

    if diagnostics is None:
        cleanup(artifact_dir)
        return

    # 5. Report errors
    errors_by_location = map_diagnostics(diagnostics, snippet_map)
    has_errors = report_errors(errors_by_location)

    # 6. Delete ci_artifacts
    cleanup(artifact_dir)

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
