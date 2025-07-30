import typer
from typing_extensions import Annotated
import json
from fastapi import FastAPI, Path, HTTPException
from gitingest import ingest

from typing import Tuple, Optional

from collections import OrderedDict
import tempfile
import os
import re
import sys
import urllib.parse
import toml
from pathlib import Path as PathLib
import ast


cli = typer.Typer()
api = FastAPI()

RELEVANT_FILES = ("requirements.txt", "pyproject.toml", "setup.py")

# Helper to extract dependencies from requirements.txt


def parse_requirements_txt(content: str) -> list[str]:
    deps = []
    # print(f"Parsing requirements.txt content:\n{content}")
    for line in content.splitlines():
        line = line.strip()
        # print(f"Processing line: '{line}'")
        if not line or line.startswith("#"):
            # print(f"Skipping line (empty or comment): '{line}'")
            continue
        # Preserve lines with environment markers
        if ";" in line:
            # print(f"Adding line with environment marker: '{line}'")
            deps.append(line)
            continue
        # Remove version specifiers for other lines
        # Split on any of these version specifiers: ==, >=, <=, !=, ~=, >, <, ===
        dep = re.split(r"==|>=|<=|!=|~=|>|<|===", line)[0].strip()
        if dep:
            # print(f"Adding dependency: '{dep}' (from line: '{line}')")
            deps.append(dep)
    # print(f"Final dependencies list: {deps}")
    return deps


# Helper to extract dependencies from pyproject.toml


def parse_pyproject_toml(content: str) -> list[str]:
    deps = []
    # Try to parse as TOML for robust extraction
    try:
        data = toml.loads(content)

        # Handle poetry dependencies
        if (
            "tool" in data
            and "poetry" in data["tool"]
            and "dependencies" in data["tool"]["poetry"]
        ):
            poetry_deps = data["tool"]["poetry"]["dependencies"]
            deps.extend(
                [
                    dep
                    for dep in poetry_deps.keys()
                    if dep != "python"  # Skip python version requirement
                ]
            )

        # PEP 621: [project] dependencies
        if "project" in data and "dependencies" in data["project"]:
            project_deps = data["project"]["dependencies"]
            # Handle both list and dict formats
            if isinstance(project_deps, list):
                deps.extend(
                    [
                        re.split(r"==|>=|<=|!=|~=|>|<|===", dep)[0].strip()
                        for dep in project_deps
                    ]
                )
            elif isinstance(project_deps, dict):
                deps.extend([dep for dep in project_deps.keys() if dep != "python"])

        # Handle build-system requires
        if "build-system" in data and "requires" in data["build-system"]:
            build_deps = data["build-system"]["requires"]
            deps.extend(
                [
                    re.split(r"==|>=|<=|!=|~=|>|<|===", dep)[0].strip()
                    for dep in build_deps
                ]
            )

    except Exception:
        # print(f"Error parsing pyproject.toml: {e}")
        return []

    return list(set(deps))  # Remove duplicates


# Helper to extract dependencies from setup.py


def parse_setup_py(content: str) -> tuple[list[str], str | None]:
    """Parse setup.py for install_requires and python_requires, even if defined as variables or passed as variables."""
    deps = []
    py_version = None
    var_map = {}
    try:
        tree = ast.parse(content)
        # Track variable assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Only store lists/tuples of strings
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            values = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    values.append(elt.s)
                                elif isinstance(elt, ast.Constant) and isinstance(
                                    elt.value, str
                                ):
                                    values.append(elt.value)
                            var_map[target.id] = values
                        # Also store string assignments (for python_requires)
                        elif isinstance(node.value, ast.Str):
                            var_map[target.id] = node.value.s
                        elif isinstance(node.value, ast.Constant) and isinstance(
                            node.value.value, str
                        ):
                            var_map[target.id] = node.value.value
        # Find setup() call
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "id")
                and node.func.id == "setup"
            ):
                for kw in node.keywords:
                    if kw.arg == "install_requires":
                        # Direct list/tuple
                        if isinstance(kw.value, (ast.List, ast.Tuple)):
                            for elt in kw.value.elts:
                                if isinstance(elt, ast.Str):
                                    deps.append(elt.s)
                                elif isinstance(elt, ast.Constant) and isinstance(
                                    elt.value, str
                                ):
                                    deps.append(elt.value)
                        # Variable reference
                        elif isinstance(kw.value, ast.Name):
                            var_name = kw.value.id
                            if var_name in var_map and isinstance(
                                var_map[var_name], list
                            ):
                                deps.extend(var_map[var_name])
                    if kw.arg == "python_requires":
                        if isinstance(kw.value, ast.Str):
                            py_version = kw.value.s
                        elif isinstance(kw.value, ast.Constant) and isinstance(
                            kw.value.value, str
                        ):
                            py_version = kw.value.value
                        elif isinstance(kw.value, ast.Name):
                            var_name = kw.value.id
                            if var_name in var_map and isinstance(
                                var_map[var_name], str
                            ):
                                py_version = var_map[var_name]
    except Exception:
        # fallback: regex
        match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if match:
            items = match.group(1)
            for dep in re.findall(r'"([^"]+)"|\'([^\']+)\'', items):
                dep_name = dep[0] or dep[1]
                if dep_name:
                    deps.append(dep_name)
        match_py = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
        if match_py:
            py_version = match_py.group(1)
    return deps, py_version


def extract_package_name_from_setup_py(content: str) -> str:
    # First, try to find name="<package_name>"
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
    if name_match:
        return name_match.group(1)

    # If name is not a literal, fall back to packages=['<package_name>']
    # Find packages=[...]
    packages_match = re.search(r"packages\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if packages_match:
        # Extract the first string literal from the list
        package_list_str = packages_match.group(1)
        first_package_match = re.search(r'["\']([^"\']+)["\']', package_list_str)
        if first_package_match:
            return first_package_match.group(1)

    return None


def extract_package_name_from_pyproject_toml(content: str) -> str:
    match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def is_github_repo(repo_name: str) -> Tuple[bool, Optional[str]]:
    """Check if a string represents a valid GitHub repository.
    Returns (is_valid, normalized_name)"""
    # Handle GitHub URLs
    if repo_name.startswith("https://github.com/"):
        parsed = urllib.parse.urlparse(repo_name)
        path = parsed.path.strip("/")
        if path.count("/") >= 1:
            owner_repo = "/".join(path.split("/")[:2])
            return True, owner_repo

    return False, None


def handle_local_directory(dir_path: str) -> dict:
    """Handle analysis of a local directory."""
    dir_path = PathLib(dir_path).resolve()
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {dir_path}")
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")

    dependencies = set()
    py_version = None
    package_name = None

    # Look for dependency files
    for file_name in RELEVANT_FILES:
        file_path = dir_path / file_name
        if not file_path.exists() or not file_path.is_file():
            continue

        try:
            with open(file_path, "r") as f:
                file_content = f.read()

            match file_name:
                case "requirements.txt":
                    dependencies.update(parse_requirements_txt(file_content))
                case "pyproject.toml":
                    dependencies.update(parse_pyproject_toml(file_content))
                    m = re.search(r'python\s*=\s*"([^"]+)"', file_content)
                    if m:
                        py_version = m.group(1)
                    if not package_name:
                        package_name = extract_package_name_from_pyproject_toml(
                            file_content
                        )
                case "setup.py":
                    dependencies.update(parse_setup_py(file_content)[0])
                    if not package_name:
                        package_name = extract_package_name_from_setup_py(file_content)
        except Exception:
            # print(f"Error parsing {file_path}: {e}")
            continue

    # Remove python version specifiers from dependencies
    dep_list = sorted(
        set(d for d in dependencies if not re.match(r"^python([<>=!~].*)?$", d))
    )

    if not py_version:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    # Compose the command
    if dep_list:
        if package_name:
            one_liner = f"uv run --python '{py_version}' --with '{','.join(dep_list + [package_name])}' python -c 'import {package_name}; print({package_name})'"
        else:
            one_liner = (
                f"uv run --python '{py_version}' --with '{','.join(dep_list)}' python"
            )
    else:
        if package_name:
            one_liner = f"uv run --python '{py_version}' python -c 'import {package_name}; print({package_name})'"
        else:
            one_liner = f"uv run --python '{py_version}' python"

    return {
        "oneLiner": one_liner,
        "dependencies": dep_list,
        "packageName": package_name,
        "pythonVersion": py_version,
        "isLocal": True,
    }


def detect_project_source(source: str) -> tuple[str, bool]:
    """Detect if the source is a GitHub repo or a local directory.
    Returns (normalized_source, is_github)
    """
    # GitHub URL
    if source.startswith("https://github.com/"):
        parsed = urllib.parse.urlparse(source)
        path = parsed.path.strip("/")
        if path.count("/") >= 1:
            owner_repo = "/".join(path.split("/")[:2])
            return owner_repo, True
    # owner/repo format
    if "/" in source and not source.startswith("/"):
        owner_repo = "/".join(source.split("/")[:2])
        return owner_repo, True
    # Otherwise, treat as local directory
    return source, False


def extract_project_files_multi(source: str, is_github: bool) -> list[dict]:
    """Extract all relevant files and their parsed info from a repo or local dir."""
    found_files = []
    files_content = {}
    if is_github:
        repo_url = f"https://github.com/{source}"
        with tempfile.TemporaryDirectory() as _:
            if ingest:
                # print(f"Ingesting from {repo_url}")
                summary, tree, content = ingest(
                    repo_url,
                    include_patterns=set(RELEVANT_FILES),
                )
                # print(f"Content type: {type(content)}")
                # print(f"Content preview:\n{content[:500]}")

                if isinstance(content, str):
                    content_dict = OrderedDict()

                    # First, find all FILE: markers and their content
                    current_file = None
                    current_content = []

                    for line in content.splitlines():
                        if line.startswith("FILE:"):
                            # If we were collecting content for a previous file, save it
                            if current_file and current_content:
                                file_content = "\n".join(current_content).strip()
                                if any(
                                    current_file.endswith(fname)
                                    for fname in RELEVANT_FILES
                                ):
                                    # print(f"Saving content for {current_file}")
                                    content_dict[current_file] = file_content

                            # Start new file
                            current_file = line.replace("FILE:", "").strip()
                            current_content = []
                            # print(f"Found file: {current_file}")
                        elif line.startswith("="):
                            # Skip separator lines
                            continue
                        elif line.startswith("SYMLINK:"):
                            # Skip symlink blocks
                            current_file = None
                            current_content = []
                        elif current_file:
                            # Collect content lines for current file
                            current_content.append(line)

                    # Don't forget to save the last file
                    if current_file and current_content:
                        file_content = "\n".join(current_content).strip()
                        if any(
                            current_file.endswith(fname) for fname in RELEVANT_FILES
                        ):
                            # print(f"Saving content for {current_file}")
                            content_dict[current_file] = file_content

                    # print(f"\nFound {len(content_dict)} relevant files: {list(content_dict.keys())}")
                    files_content = content_dict
                else:
                    # Handle case where content is already a dict
                    # print("Content is a dict, processing directly")
                    for k, v in content.items():
                        if any(k.endswith(fname) for fname in RELEVANT_FILES):
                            # print(f"Found relevant file in dict: {k}")
                            files_content[k] = v
    else:
        dir_path = PathLib(source).resolve()
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Directory does not exist: {dir_path}")
        for root, dirs, files in os.walk(dir_path):
            for fname in files:
                if fname in RELEVANT_FILES:
                    file_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(file_path, dir_path)
                    with open(file_path, "r") as f:
                        files_content[rel_path] = f.read()
    # Now parse each file
    for rel_path, file_content in files_content.items():
        # print(f"\nProcessing file: {rel_path}")
        # print(f"Content preview: {file_content[:100]}")
        file_type = None
        dependencies = []
        py_version = None
        package_name = None
        if rel_path.endswith("requirements.txt"):
            file_type = "requirements.txt"
            dependencies = parse_requirements_txt(file_content)
            # print(f"Found dependencies in requirements.txt: {dependencies}")
        elif rel_path.endswith("pyproject.toml"):
            file_type = "pyproject.toml"
            dependencies = parse_pyproject_toml(file_content)
            m = re.search(r'python\s*=\s*"([^"]+)"', file_content)
            if m:
                py_version = m.group(1)
            package_name = extract_package_name_from_pyproject_toml(file_content)
            # print(f"Found dependencies in pyproject.toml: {dependencies}")
        elif rel_path.endswith("setup.py"):
            file_type = "setup.py"
            dependencies, py_version = parse_setup_py(file_content)
            package_name = extract_package_name_from_setup_py(file_content)
            # print(f"Found dependencies in setup.py: {dependencies}")

        # Remove python version specifiers from dependencies
        dep_list = sorted(
            set(d for d in dependencies if not re.match(r"^python([<>=!~].*)?$", d))
        )
        # print(f"Final dependency list: {dep_list}")

        # Compose the command
        if dep_list:
            if package_name:
                one_liner = f"uv run --python '{py_version or sys.version_info.major}.{sys.version_info.minor}' --with '{','.join(dep_list + [package_name])}' python -c 'import {package_name}; print({package_name})'"
            else:
                one_liner = f"uv run --python '{py_version or sys.version_info.major}.{sys.version_info.minor}' --with '{','.join(dep_list)}' python"
        else:
            if package_name:
                one_liner = f"uv run --python '{py_version or sys.version_info.major}.{sys.version_info.minor}' python -c 'import {package_name}; print({package_name})'"
            else:
                one_liner = f"uv run --python '{py_version or sys.version_info.major}.{sys.version_info.minor}' python"
        uv_install_from_git_command = None
        if is_github:
            uv_install_from_git_command = f"uv run --with 'git+https://github.com/{source}' --python '{py_version or sys.version_info.major}.{sys.version_info.minor}' python"

        found_files.append(
            {
                "file": rel_path,
                "fileType": file_type,
                "oneLiner": one_liner,
                "uvInstallFromSource": uv_install_from_git_command,
                "dependencies": dep_list,
                "packageName": package_name,
                "pythonVersion": py_version
                or f"{sys.version_info.major}.{sys.version_info.minor}",
                "isLocal": not is_github,
            }
        )
    return found_files


def _analyze_repo_logic(source: str) -> list[dict]:
    normalized_source, is_github = detect_project_source(source)
    return extract_project_files_multi(normalized_source, is_github)


@cli.command()
def analyze_repo(
    repo_name: Annotated[
        str,
        typer.Argument(
            help="GitHub repository (owner/repo or URL) or path to local directory"
        ),
    ],
):
    try:
        result = _analyze_repo_logic(repo_name)
        print(json.dumps(result, indent=4))
        return result
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


@api.get("/{repo_name:path}")
def analyze_repo_api(
    repo_name: str = Path(
        ...,
        description="GitHub repository (owner/repo or URL) or path to local directory",
    ),
):
    try:
        return _analyze_repo_logic(repo_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    cli()
