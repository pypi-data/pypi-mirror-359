import os

from goblin.analyzer import parse_java_file


def test_parse_example_test_file():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples/ExampleTest.java"))
    test_class = parse_java_file(file_path)

    assert test_class.class_name == "ExampleTest"
    assert len(test_class.methods) == 8

    test_method = test_class.methods[0]
    assert test_method.method_name == "testAddition"
    assert test_method.assertion_count == 1

    assert len(test_method.smells) == 0