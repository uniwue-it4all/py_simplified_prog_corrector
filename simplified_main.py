#!/usr/bin/env python3

import sys
from io import StringIO
from traceback import format_exc as traceback_format_exc
from typing import List, Any, Dict

# noinspection PyUnresolvedReferences
from test_main import test, convert_base_data, convert_test_input

from test_base import SingleTestResult, CompleteTestResult


class SimplifiedResult(SingleTestResult):
    def __init__(self, test_id: int, test_input: Any, awaited: Any, gotten: Any, success: str, stdout: str):
        self.test_id: int = test_id
        self.test_input: Any = test_input
        self.awaited: Any = awaited
        self.gotten: Any = gotten
        self.success: str = success
        self.stdout: str = stdout

    def to_json_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "test_input": self.test_input,
            "awaited": self.awaited,
            "gotten": self.gotten,
            "success": self.success,
            "stdout": self.stdout
        }


class SimplifiedCompleteResult(CompleteTestResult[SimplifiedResult]):
    def __init__(self, results: List[SimplifiedResult], result_type: str, errors: str):
        super().__init__(results)
        self.result_type: str = result_type
        self.errors: str = errors

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "results": list(map(lambda r: r.to_json_dict(), self.results)),
            "result_type": self.result_type,
            "errors": self.errors
        }


def perform_test(base_data: Any, test_data: Any) -> SimplifiedResult:
    test_id: int = test_data['id']
    test_input: Any = test_data['input']
    awaited_output: Any = test_data['output']

    # Convert input
    converted_input: Any = convert_test_input(base_data, test_input)

    # Redirect stdout to variable test_stdout
    sys.stdout = test_stdout = StringIO()

    # noinspection PyBroadException
    try:
        gotten_output, correctness = test(base_data, converted_input, awaited_output)
        success = 'COMPLETE' if correctness else 'NONE'
    except:
        gotten_output = traceback_format_exc()
        success = 'ERROR'

    # Revert stdout to 'normal' stdout
    sys.stdout = sys.__stdout__

    return SimplifiedResult(test_id, test_input, awaited_output, gotten_output, success, test_stdout.getvalue())


def main_test(complete_test_data: Any) -> List[SimplifiedResult]:
    base_data = None
    if 'baseData' in complete_test_data:
        base_data = convert_base_data(complete_test_data['baseData'])

    test_results: List[SimplifiedResult] = []

    for test_data in complete_test_data['testdata']:
        single_result: SimplifiedResult = perform_test(base_data, test_data)
        test_results.append(single_result)

    return test_results


def test_simplified(test_data) -> object:
    try:
        results: List[SimplifiedResult] = main_test(test_data)
        result_type: str = 'run_through'
        errors: str = ''
    except SyntaxError:
        results = []
        result_type = 'syntax_error'
        errors = traceback_format_exc()

    return SimplifiedCompleteResult(results, result_type, errors)