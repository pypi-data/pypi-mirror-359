from enum import Enum


class SmellType(str, Enum):
    NO_ASSERTIONS = "No assertions found in test method"
    TODO_ANNOTATION = "Unresolved TODO annotation"
    DISABLED_ANNOTATION = "Disabled test annotation, consider cleaning up"
    IGNORE_ANNOTATION = "Ignore annotation, consider cleaning up"
    MISSING_TEST_ANNOTATION = "Missing @Test annotation in test-like method"

    @classmethod
    def print_available_smell_types(cls):
        print("Available smell types:")
        for smell in cls:
            print(f"- {smell.value}")