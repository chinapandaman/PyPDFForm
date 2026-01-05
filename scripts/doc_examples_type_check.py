import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

import yaml


def main():
    # 1. Create ci_artifacts
    artifact_dir = "ci_artifacts"
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)

    # Create pyrightconfig.json to ignore root pyproject.toml and set python path
    with open(os.path.join(artifact_dir, "pyrightconfig.json"), "w") as f:
        json.dump({"extraPaths": [".."]}, f)

    # 2. Look up docs under User Guide
    with open("mkdocs.yml", "r") as f:
        content = f.read()

    # Remove custom python tags that cause yaml.safe_load to fail
    content = re.sub(r"!!python/name:[\w\.]+", "null", content)

    config = yaml.safe_load(content)

    user_guide_docs = []
    nav = config.get("nav", [])
    for item in nav:
        if isinstance(item, dict) and "User Guide" in item:
            user_guide_docs = item["User Guide"]
            break

    snippet_map = {}  # filename -> (doc_path, start_line_in_doc)
    snippet_idx = 0

    for doc_file in user_guide_docs:
        if not isinstance(doc_file, str):
            continue

        doc_path = os.path.join("docs", doc_file)
        if not os.path.exists(doc_path):
            continue

        with open(doc_path, "r") as f:
            lines = f.readlines()

        in_code_block = False
        code_lines = []
        start_line = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check for python code block
            if stripped.startswith("```python"):
                in_code_block = True
                start_line = i + 1  # 1-based index (line with ```python)
                code_lines = []
            elif stripped.startswith("```") and in_code_block:
                in_code_block = False

                # Check if snippet is empty
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

    # 4. Run pyright
    cmd = [
        "pyright",
        "--outputjson",
        "--project",
        os.path.join(artifact_dir, "pyrightconfig.json"),
        artifact_dir,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        print("Failed to decode pyright output")
        # cleanup
        if os.path.exists(artifact_dir):
            shutil.rmtree(artifact_dir)
        return

    diagnostics = data.get("generalDiagnostics", [])

    # 5. Report errors
    errors_by_location = {}  # doc_path -> {line_num -> [messages]}

    for diag in diagnostics:
        file_path = diag.get("file")
        filename = os.path.basename(file_path)

        if filename in snippet_map:
            original_doc, start_line = snippet_map[filename]

            error_line_in_snippet = diag["range"]["start"]["line"]
            # start_line is the line with ```python
            # line 0 of snippet is start_line + 1
            original_line = start_line + 1 + error_line_in_snippet

            msg = diag.get("message", "")

            if original_doc not in errors_by_location:
                errors_by_location[original_doc] = {}
            if original_line not in errors_by_location[original_doc]:
                errors_by_location[original_doc][original_line] = []

            errors_by_location[original_doc][original_line].append(msg)

    # Print consolidated errors
    has_errors = False
    for doc_path in sorted(errors_by_location.keys()):
        for line_num in sorted(errors_by_location[doc_path].keys()):
            has_errors = True
            messages = errors_by_location[doc_path][line_num]
            print(f"{doc_path}:{line_num}")
            for m in messages:
                print(f"  {m}")

    # 6. Delete ci_artifacts
    if os.path.exists(artifact_dir):
        shutil.rmtree(artifact_dir)

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
