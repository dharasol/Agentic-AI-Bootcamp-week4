
from dotenv import load_dotenv
load_dotenv()

from reviewer_agent import (
    get_offline_mock_bug_analysis,
    get_offline_mock_fix,
    get_offline_mock_judge,
)

SAMPLE_CODE = """
def divide(a, b):
    return a / b
"""

def test_offline_bug_analysis_detects_division():
    result = get_offline_mock_bug_analysis(SAMPLE_CODE)
    print(f"\n[offline_analysis] {result}")
    assert isinstance(result, dict)
    assert "bug_description" in result
    assert "root_cause" in result
    assert result["severity"] == "high"

def test_offline_bug_analysis_generic_code():
    result = get_offline_mock_bug_analysis("x = input()")
    print(f"\n[offline_analysis_generic] {result}")
    assert isinstance(result, dict)
    assert result["severity"] == "medium"

def test_offline_fix_generates_zero_guard():
    analysis = get_offline_mock_bug_analysis(SAMPLE_CODE)
    fix = get_offline_mock_fix(SAMPLE_CODE, analysis)
    print(f"\n[offline_fix]\n{fix}")
    assert fix is not None
    assert len(fix) > 10
    assert "def divide" in fix
    assert "b == 0" in fix

def test_offline_judge_returns_score():
    analysis = get_offline_mock_bug_analysis(SAMPLE_CODE)
    result = get_offline_mock_judge(analysis)
    print(f"\n[offline_judge] {result}")
    assert isinstance(result, dict)
    assert "correctness" in result
    score = result["correctness"]
    assert 0 <= score <= 10

def test_offline_fix_is_executable():
    analysis = get_offline_mock_bug_analysis(SAMPLE_CODE)
    fix = get_offline_mock_fix(SAMPLE_CODE, analysis)
    try:
        compile(fix, "<string>", "exec")
    except SyntaxError as e:
        assert False, f"Generated fix has syntax error: {e}"

def test_offline_fix_actually_works():
    analysis = get_offline_mock_bug_analysis(SAMPLE_CODE)
    fix = get_offline_mock_fix(SAMPLE_CODE, analysis)
    namespace = {}
    exec(fix, namespace)
    divide = namespace["divide"]
    assert divide(10, 2) == 5.0
    assert divide(10, 0) == 0
