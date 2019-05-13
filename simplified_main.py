#!/usr/bin/env python3

import sys
from io import StringIO
from traceback import format_exc as traceback_format_exc
from typing import List, Any, Dict

# noinspection PyUnresolvedReferences
from test_main import test, convert_base_data, convert_test_input


class SingleSimplifiedTestData:
    def __init__(self, id: int, input: List[Any], output: Any):
        self.id: int = id
        self.input: List[Any] = input
        self.output: Any = output


class TestData:
    def __init__(self, base_data: Any, single_test_data: List[SingleSimplifiedTestData]):
        self.base_data: Any = base_data
        self.single_test_data: List[SingleSimplifiedTestData] = single_test_data


class SimplifiedResult:
    def __init__(self, test_id: int, test_input: Any, awaited: Any, gotten: Any, success: str, stdout: str):
        self.test_id: int = test_id
        self.test_input: Any = test_input
        self.awaited: Any = awaited
        self.gotten: Any = gotten
        self.success: str = success
        self.stdout: str = stdout

    def to_json_dict(self) -> Dict:
        return {
            "id": self.test_id,
            "input": self.test_input,
            "awaited": self.awaited,
            "gotten": self.gotten,
            "success": self.success,
            "stdout": self.stdout
        }


class CompleteResult:
    def __init__(self, results: List[SimplifiedResult], result_type: str, errors: str):
        self.results: List[SimplifiedResult] = results
        self.result_type: str = result_type
        self.errors: str = errors

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "results": list(map(lambda r: r.to_json_dict(), self.results)),
            "resultType": self.result_type,
            "errors": self.errors
        }


def read_test_data_from_json_dict(json_dict: Dict) -> TestData:
    base_data: Any = None
    if 'baseData' in json_dict:
        base_data = json_dict['baseData']

    single_test_data: List[SingleSimplifiedTestData] = []

    for single_td_json in json_dict['testData']:
        single_td = SingleSimplifiedTestData(int(single_td_json['id']), single_td_json['input'],
                                             single_td_json['output'])
        single_test_data.append(single_td)

    return TestData(base_data, single_test_data)


def perform_test(base_data: Any, test_data: SingleSimplifiedTestData) -> SimplifiedResult:
    test_input: Any = test_data.input
    awaited_output: Any = test_data.output

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

    return SimplifiedResult(test_data.id, test_input, awaited_output, gotten_output, success, test_stdout.getvalue())


def main_test(complete_test_data: TestData) -> List[SimplifiedResult]:
    base_data = None
    if complete_test_data.base_data is not None:
        base_data = convert_base_data(complete_test_data.base_data)

    test_results: List[SimplifiedResult] = []

    for test_data in complete_test_data.single_test_data:
        single_result: SimplifiedResult = perform_test(base_data, test_data)
        test_results.append(single_result)

    return test_results


def test_simplified(test_data: TestData) -> CompleteResult:
    try:
        results: List[SimplifiedResult] = main_test(test_data)
        result_type: str = 'run_through'
        errors: str = ''
    except SyntaxError:
        results = []
        result_type = 'syntax_error'
        errors = traceback_format_exc()

    return CompleteResult(results, result_type, errors)
