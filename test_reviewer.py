import pytest
import json
import ast
from typing import Any, cast
from unittest.mock import patch, MagicMock
from tracer import Tracer
import reviewer_agent

def test_tracer_metrics():
    """Validates that tracer correctly measures duration and profiles bottlenecks"""
    t = Tracer("test_session", "test/repo")
    t.start_stage("stage_a")
    t.end_stage("stage_a")
    bottlenecks = t.get_bottlenecks()
    assert len(bottlenecks) == 1
    assert bottlenecks[0]["stage"] == "stage_a"

@patch("reviewer_agent.openai_client.chat.completions.create")
def test_bug_analysis(mock_openai):
    """Ensures bug analysis accurately reports structural JSON formatting properties"""
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "bug_description": "ZeroDivisionError in division wrapper module",
        "location": "line 2",
        "severity": "critical",
        "root_cause": "Missing denominator boundaries filtering rules",
        "suggested_fix_approach": "Inject error exceptions handling fallback constraints"
    })
    mock_openai.return_value.choices = [mock_response]
    
    analysis = reviewer_agent.analyze_bug("def run(): return 1/0")
    if isinstance(analysis, str):
        analysis = json.loads(analysis)
    analysis = cast(dict[str, Any], analysis)
    assert "severity" in analysis
    assert "bug_description" in analysis
    assert analysis["severity"] == "critical"

@patch("reviewer_agent.anthropic_client.messages.create")
def test_fix_generation(mock_anthropic):
    """Verifies that generated code edits present clean syntax outputs"""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="def run():\n    return 1")]
    mock_anthropic.return_value = mock_response

    generated_code = reviewer_agent.generate_fix("def run(): return 1/0", "ZeroDivisionError")
    ast.parse(generated_code)

