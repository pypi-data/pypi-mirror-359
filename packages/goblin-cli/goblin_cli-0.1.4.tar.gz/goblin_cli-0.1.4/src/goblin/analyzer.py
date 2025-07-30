from dataclasses import dataclass, field
from typing import List

import javalang

from goblin.detector import detect_smells
from goblin.smell_types import SmellType


@dataclass
class MethodInfo:
    class_name: str
    method_name: str
    annotations: List[str]
    assertion_count: int
    smells: List[SmellType] = field(default_factory=list)

@dataclass
class ClassInfo:
    class_name: str
    methods: List[MethodInfo]

def parse_java_file(file_path: str) -> ClassInfo:
    with open(file_path, 'r') as file:
        source_code = file.read()

    tree = javalang.parse.parse(source_code)
    class_declaration = next(
        (node for path, node in tree.filter(javalang.tree.ClassDeclaration)), None
    )

    if not class_declaration:
        raise ValueError("No class declaration found.")

    test_methods = []

    for method in class_declaration.methods:
        method_name = method.name
        annotations = [annotation.name for annotation in method.annotations]
        body = method.body or []

        # Count how many assertion lines there are
        assertion_count = sum(
            1 for statement in body
            if isinstance(statement, javalang.tree.StatementExpression) and
               hasattr(statement.expression, 'member') and
               "assert" in statement.expression.member.lower()
        )

        test_method = MethodInfo(
            class_name=class_declaration.name,
            method_name=method_name,
            annotations=annotations,
            assertion_count=assertion_count
        )
        test_method.smells = detect_smells(test_method)
        test_methods.append(test_method)

    return ClassInfo(
        class_name=class_declaration.name,
        methods=test_methods
    )