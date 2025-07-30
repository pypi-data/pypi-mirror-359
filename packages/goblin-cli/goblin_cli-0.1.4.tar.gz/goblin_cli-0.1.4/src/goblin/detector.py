import re
from goblin.smell_types import SmellType

IGNORED_NAME_PATTERNS = [
    r"^setup", r"^helper", r"^init", r"^cleanup", r"^tearDown"
]

def smell_no_assertions(method):
    if "TEST" in [a.upper() for a in method.annotations]:
        if method.assertion_count == 0:
            return SmellType.NO_ASSERTIONS

def smell_todo_annotation(method):
    if "TODO" in [a.upper() for a in method.annotations]:
        return SmellType.TODO_ANNOTATION

def smell_disabled(method):
    if "DISABLED" in [a.upper() for a in method.annotations]:
        return SmellType.DISABLED_ANNOTATION
    
def smell_ignored(method):
    if "IGNORE" in [a.upper() for a in method.annotations]:
        return SmellType.IGNORE_ANNOTATION

def smell_no_annotation(method):
    if (("TEST" in method.method_name.upper()) or method.assertion_count != 0) and ("TEST" not in [a.upper() for a in method.annotations]):
        return SmellType.MISSING_TEST_ANNOTATION

# List of all rule functions
SMELL_RULES = [
    smell_no_assertions,
    smell_todo_annotation,
    smell_disabled,
    smell_ignored,
    smell_no_annotation
]

def is_helper_method(method):
    if "TEST" in (a.upper() for a in method.annotations):
        return False
    return any(re.search(pattern, method.method_name) for pattern in IGNORED_NAME_PATTERNS)

def detect_smells(method):
    smells = []
    if is_helper_method(method):
        return smells
    for rule in SMELL_RULES:
        result = rule(method)
        if result:
            smells.append(result)
    return smells