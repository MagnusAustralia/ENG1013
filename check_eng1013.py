"""
ENG1013 Python Coding Standards Checker.

Checks Python files against the ENG1013 coding standards:

- File headers
- Variable naming using lower camelCase
- Function naming using snake_case
- Descriptive variable and function names
- Function documentation
- Four-space indentation
- Global variable placement
- Basic magic-number detection
"""

import ast
import keyword
import re
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

# Required fields in the file header.
REQUIRED_FILE_HEADER_FIELDS = ["Created By", "Created Date", "Version"]


# These numbers are generally acceptable without explanation.
ALLOWED_MAGIC_NUMBERS = {0, 1, 2, -1}


# Variable names must start with a lowercase letter.
# Subsequent words should begin with an uppercase letter.
#
# Examples:
#   buildingHeight
#   numberOfInputs
#   radius
#
# Not allowed:
#   BuildingHeight
#   building_height
#   building_Height
VARIABLE_NAME_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9]*$")


# Function names must use lowercase snake_case.
#
# Examples:
#   find_max_number
#   calculate_area
#
# Not allowed:
#   findMaxNumber
#   Find_Max_Number
#   find_Max_Number
FUNCTION_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


# Names which are commonly too vague for the ENG1013 standard.
#
# This is intentionally a small list because a computer cannot
# reliably determine whether every name is descriptive.
AMBIGUOUS_NAMES = {"x", "y", "z", "a", "b", "c", "i", "j", "k", "fx"}


# Python names that are not variables.
SPECIAL_NAMES = {"self", "cls"}


# ============================================================
# Naming checks
# ============================================================


def is_camel_case(name):
    """Return True when name follows lower camelCase."""
    return bool(VARIABLE_NAME_PATTERN.fullmatch(name))


def is_snake_case(name):
    """Return True when name follows snake_case."""
    return bool(FUNCTION_NAME_PATTERN.fullmatch(name))


def is_descriptive_name(name):
    """Return True when a name is not obviously ambiguous."""
    return name not in AMBIGUOUS_NAMES


def check_variable_name(name, filename, line_number):
    """
    Check a variable name against the ENG1013 naming standard.

    Variables must use lower camelCase.
    """
    errors = []

    # Ignore Python keywords.
    if keyword.iskeyword(name):
        return errors

    # Ignore private/special names.
    if name.startswith("_"):
        return errors

    # Ignore self and cls.
    if name in SPECIAL_NAMES:
        return errors

    # Ignore constants written in UPPER_CASE.
    #
    # This allows examples such as:
    # MAX_VALUE = 100
    if name.isupper():
        return errors

    if not is_camel_case(name):
        errors.append(f"{filename}:{line_number}: variable '{name}' must use lower camelCase.")

    if not is_descriptive_name(name):
        errors.append(f"{filename}:{line_number}: variable '{name}' may not be descriptive enough.")

    return errors


def check_function_name(name, filename, line_number):
    """
    Check a function name against the ENG1013 naming standard.

    Functions must use lowercase snake_case.
    """
    errors = []

    # Ignore Python special methods such as __init__.
    if name.startswith("__") and name.endswith("__"):
        return errors

    if not is_snake_case(name):
        errors.append(f"{filename}:{line_number}: function '{name}' must use snake_case.")

    if not is_descriptive_name(name):
        errors.append(f"{filename}:{line_number}: function '{name}' may not be descriptive enough.")

    return errors


# ============================================================
# File header checks
# ============================================================


def check_file_header(lines, filename):
    """
    Check that the Python file starts with a # comment header.

    The header must contain:
        Created By
        Created Date
        Version
    """
    errors = []

    if not lines:
        errors.append(f"{filename}: file is empty.")
        return errors

    header_lines = []

    # Look only at the first 15 lines.
    for line in lines[:15]:
        stripped_line = line.strip()

        if stripped_line.startswith("#"):
            header_lines.append(stripped_line)

        elif stripped_line == "":
            continue

        else:
            break

    if not header_lines:
        errors.append(f"{filename}: missing file header using # comments.")
        return errors

    header_text = "\n".join(header_lines).lower()

    for required_field in REQUIRED_FILE_HEADER_FIELDS:
        if required_field.lower() not in header_text:
            errors.append(f"{filename}: file header is missing '{required_field}'.")

    return errors


# ============================================================
# Indentation checks
# ============================================================


def check_indentation(lines, filename):
    """
    Check that indentation uses spaces in multiples of four.

    Tabs are not allowed.
    """
    errors = []

    for line_number, line in enumerate(lines, start=1):
        # Ignore completely blank lines.
        if not line.strip():
            continue

        if "\t" in line:
            errors.append(f"{filename}:{line_number}: tabs are not allowed; use four spaces.")

        leading_spaces = len(line) - len(line.lstrip(" "))

        if leading_spaces % 4 != 0:
            errors.append(f"{filename}:{line_number}: indentation must use multiples of four spaces.")

    return errors


# ============================================================
# Function documentation checks
# ============================================================


def check_function_header(node, filename):
    """
    Check that a function contains a docstring.

    Both single-line and multi-line docstrings are accepted.

    Valid:

        def calculate_area(radius):
            \"\"\"Calculate the area.\"\"\"

    Also valid:

        def calculate_area(radius):
            \"\"\"
            Calculate the area.

            Parameters:
            radius (float): The circle radius.

            Returns:
            float: The area.
            \"\"\"
    """
    errors = []

    docstring = ast.get_docstring(node)

    if docstring is None:
        errors.append(f"{filename}:{node.lineno}: function '{node.name}' is missing a function header/docstring.")

    return errors


# ============================================================
# Global variable checks
# ============================================================


def is_global_assignment(node):
    """Return True when an AST node assigns a global variable."""
    return isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))


def check_globals(nodes, filename):
    """
    Check that global variables are declared before functions.

    This treats assignments at module level as global variables.
    """
    errors = []

    function_found = False

    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            function_found = True

        elif is_global_assignment(node):
            if function_found:
                errors.append(
                    f"{filename}:{node.lineno}: "
                    "global variable declared after a function. "
                    "Globals should be declared near the top "
                    "of the file."
                )

    return errors


# ============================================================
# Magic-number checks
# ============================================================


def check_magic_numbers(tree, filename):
    """
    Detect obvious numeric literals used directly in expressions.

    This is intentionally conservative because a program cannot
    reliably determine whether every number is a magic number.
    """
    errors = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue

        if not isinstance(node.value, (int, float)):
            continue

        # bool is a subclass of int.
        if isinstance(node.value, bool):
            continue

        # Allow commonly harmless numbers.
        if node.value in ALLOWED_MAGIC_NUMBERS:
            continue

        parent = getattr(node, "parent", None)

        # A number assigned to a variable is considered explained.
        if isinstance(parent, (ast.Assign, ast.AnnAssign)):
            continue

        # Numbers used as default parameter values can be intentional.
        if isinstance(parent, ast.arg):
            continue

        errors.append(
            f"{filename}:{node.lineno}: "
            f"possible magic number '{node.value}'. "
            "Consider assigning it to a well-named variable."
        )

    return errors


# ============================================================
# AST helpers
# ============================================================


def attach_parents(tree):
    """
    Attach a parent reference to every AST node.

    This is used by the magic-number checker.
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


# ============================================================
# AST variable checks
# ============================================================


def check_function_arguments(node, filename):
    """Check all function parameters."""
    errors = []

    arguments = []

    arguments.extend(node.args.posonlyargs)
    arguments.extend(node.args.args)
    arguments.extend(node.args.kwonlyargs)

    if node.args.vararg is not None:
        arguments.append(node.args.vararg)

    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)

    for argument in arguments:
        # self and cls are accepted.
        if argument.arg in SPECIAL_NAMES:
            continue

        errors.extend(check_variable_name(argument.arg, filename, argument.lineno))

    return errors


def check_assignments(tree, filename):
    """Check variable names used in assignments."""
    errors = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                errors.extend(check_assignment_target(target, filename))

        elif isinstance(node, ast.AnnAssign):
            errors.extend(check_assignment_target(node.target, filename))

        elif isinstance(node, ast.AugAssign):
            errors.extend(check_assignment_target(node.target, filename))

        elif isinstance(node, ast.NamedExpr):
            errors.extend(check_assignment_target(node.target, filename))

        elif isinstance(node, ast.For):
            errors.extend(check_assignment_target(node.target, filename))

        elif isinstance(node, ast.AsyncFor):
            errors.extend(check_assignment_target(node.target, filename))

        elif isinstance(node, ast.comprehension):
            errors.extend(check_assignment_target(node.target, filename))

    return errors


def check_assignment_target(target, filename):
    """Check names appearing on the left side of assignments."""
    errors = []

    if isinstance(target, ast.Name):
        errors.extend(check_variable_name(target.id, filename, target.lineno))

    elif isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            errors.extend(check_assignment_target(element, filename))

    return errors


# ============================================================
# Individual Python file checker
# ============================================================


def check_python_file(path):
    """Run all ENG1013 checks against one Python file."""
    errors = []

    filename = str(path)

    # --------------------------------------------------------
    # Read source file
    # --------------------------------------------------------

    try:
        source = path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        errors.append(f"{filename}: could not read file as UTF-8.")
        return errors

    lines = source.splitlines()

    # --------------------------------------------------------
    # File-level checks
    # --------------------------------------------------------

    errors.extend(check_file_header(lines, filename))

    errors.extend(check_indentation(lines, filename))

    # --------------------------------------------------------
    # Parse Python
    # --------------------------------------------------------

    try:
        tree = ast.parse(source, filename=filename)

    except SyntaxError as error:
        errors.append(f"{filename}:{error.lineno}: syntax error: {error.msg}")
        return errors

    # Add parent references for AST nodes.
    attach_parents(tree)

    # --------------------------------------------------------
    # Global checks
    # --------------------------------------------------------

    errors.extend(check_globals(tree.body, filename))

    # --------------------------------------------------------
    # Variable checks
    # --------------------------------------------------------

    errors.extend(check_assignments(tree, filename))

    # --------------------------------------------------------
    # Function checks
    # --------------------------------------------------------

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            errors.extend(check_function_name(node.name, filename, node.lineno))

            errors.extend(check_function_header(node, filename))

            errors.extend(check_function_arguments(node, filename))

    # --------------------------------------------------------
    # Magic-number checks
    # --------------------------------------------------------

    errors.extend(check_magic_numbers(tree, filename))

    return errors


# ============================================================
# Find Python files
# ============================================================


def find_python_files():
    """Find Python files in the project."""
    excluded_directories = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
    }

    python_files = []

    for path in Path(".").rglob("*.py"):
        if path.name == "check_eng1013.py":
            continue

        if any(directory in path.parts for directory in excluded_directories):
            continue

        python_files.append(path)

    return sorted(python_files)


# ============================================================
# Main program
# ============================================================


def main():
    """Run the ENG1013 coding standards checker."""
    python_files = find_python_files()

    if not python_files:
        print("No Python files found.")
        return 0

    all_errors = []

    print()
    print("=" * 60)
    print("ENG1013 CODING STANDARDS CHECK")
    print("=" * 60)

    for path in python_files:
        errors = check_python_file(path)

        if errors:
            all_errors.extend(errors)

    print()

    if all_errors:
        print(f"Found {len(all_errors)} issue(s):")

        print()

        for error in all_errors:
            print(f"✗ {error}")

        print()
        print("ENG1013 check FAILED.")

        return 1

    print("✓ All ENG1013 checks passed.")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
