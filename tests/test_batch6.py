"""
Batch 6 — Understand Bug Reports & Error Logs.

Workflow tested:
  Bug Report / Error Log
          ↓
      Understand
          ↓
     Search Code
          ↓
      Read File
          ↓
   Find Root Cause
          ↓
     Propose Fix
          ↓
     Show Report

Tests:
  1. Bug report analysis: "The divide function is returning the wrong result."
  2. Error log analysis: "NameError: name 'total' is not defined"
  3. Error log with traceback analysis
  4. Undetermined cause handling ("Root cause could not be determined.")
  5. Agent end-to-end integration via agent.analyze() and agent.run()
"""

import asyncio
import os
import sys
import pytest

# Ensure utf-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── Make imports work ─────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

DEMO_ROOT = os.path.join(PROJECT_ROOT, "demo_project")

from backend.agent import Agent, AgentConfig, IssueAnalyzer, IssueReport, InputType

# ── Demo Project Setup ────────────────────────────────────────────────
BUGGY_CALCULATOR = """\"\"\"Calculator module — demo project for agent testing.

Contains an intentional bug in the divide function.
\"\"\"


def add(a: float, b: float) -> float:
    \"\"\"Return the sum of a and b.\"\"\"
    return a + b


def subtract(a: float, b: float) -> float:
    \"\"\"Return the difference of a and b.\"\"\"
    return a - b


def multiply(a: float, b: float) -> float:
    \"\"\"Return the product of a and b.\"\"\"
    return a * b


def divide(a: float, b: float) -> float:
    \"\"\"Return the quotient of a divided by b.

    BUG: This currently multiplies instead of dividing!
    \"\"\"
    return a * b  # ← BUG: should be a / b


def calculate_total(numbers: list[float]) -> float:
    \"\"\"Calculate the total of a list of numbers.

    BUG: 'total' is not defined before being used.
    \"\"\"
    return total
"""


def reset_calculator():
    """Ensure calculator.py contains both test bugs (divide and total)."""
    with open(os.path.join(DEMO_ROOT, "calculator.py"), "w", encoding="utf-8") as f:
        f.write(BUGGY_CALCULATOR)


# ══════════════════════════════════════════════════════════════════════
#  TEST 1: Bug Report Analysis
# ══════════════════════════════════════════════════════════════════════
async def _async_test_bug_report_analysis():
    reset_calculator()
    analyzer = IssueAnalyzer(project_root=DEMO_ROOT)
    bug_report_input = "The divide function is returning the wrong result."

    # Step 1: Understand
    understanding = analyzer.understand(bug_report_input)
    assert understanding.input_type == InputType.BUG_REPORT
    assert understanding.target_function == "divide"

    # Full workflow
    report = await analyzer.analyze(bug_report_input)
    rendered = report.render()

    print("\n" + "=" * 60)
    print("TEST 1: BUG REPORT ANALYSIS RESULT")
    print("=" * 60)
    print(rendered)

    # Verifications
    assert "calculator.py" in report.file_path, f"Expected calculator.py, got: {report.file_path}"
    assert "divide" in report.bug.lower()
    assert ("multiplication" in report.root_cause.lower() or "*" in report.root_cause)
    assert ("division" in report.root_cause.lower() or "/" in report.root_cause)
    assert "return a / b" in report.proposed_fix
    assert report.status == "Bug identified"

    # Verify final report structure
    assert "BUG:" in rendered
    assert "ROOT CAUSE:" in rendered
    assert "FILE:" in rendered
    assert "PROPOSED FIX:" in rendered
    assert "STATUS:\nBug identified" in rendered
    print("  ✓ Bug Report Analysis: PASS")
    return True


def test_bug_report_analysis():
    assert asyncio.run(_async_test_bug_report_analysis())


# ══════════════════════════════════════════════════════════════════════
#  TEST 2: Error Log Analysis
# ══════════════════════════════════════════════════════════════════════
async def _async_test_error_log_analysis():
    reset_calculator()
    analyzer = IssueAnalyzer(project_root=DEMO_ROOT)
    error_log_input = "NameError: name 'total' is not defined"

    # Step 1: Understand
    understanding = analyzer.understand(error_log_input)
    assert understanding.input_type == InputType.ERROR_LOG
    assert understanding.error_type == "NameError"
    assert understanding.target_symbol == "total"

    # Full workflow
    report = await analyzer.analyze(error_log_input)
    rendered = report.render()

    print("\n" + "=" * 60)
    print("TEST 2: ERROR LOG ANALYSIS RESULT")
    print("=" * 60)
    print(rendered)

    # Verifications
    assert "calculator.py" in report.file_path, f"Expected calculator.py, got: {report.file_path}"
    assert "total" in report.bug
    assert "total" in report.root_cause
    assert ("defined" in report.root_cause or "initialized" in report.root_cause)
    assert "total" in report.proposed_fix
    assert report.status == "Bug identified"

    # Verify final report structure
    assert "BUG:" in rendered
    assert "ROOT CAUSE:" in rendered
    assert "FILE:" in rendered
    assert "PROPOSED FIX:" in rendered
    assert "STATUS:\nBug identified" in rendered
    print("  ✓ Error Log Analysis: PASS")
    return True


def test_error_log_analysis():
    assert asyncio.run(_async_test_error_log_analysis())


# ══════════════════════════════════════════════════════════════════════
#  TEST 3: Traceback Error Log Analysis
# ══════════════════════════════════════════════════════════════════════
async def _async_test_traceback_error_log_analysis():
    reset_calculator()
    analyzer = IssueAnalyzer(project_root=DEMO_ROOT)
    traceback_input = """Traceback (most recent call last):
  File "calculator.py", line 34, in calculate_total
    return total
NameError: name 'total' is not defined"""

    report = await analyzer.analyze(traceback_input)
    rendered = report.render()

    print("\n" + "=" * 60)
    print("TEST 3: TRACEBACK ERROR LOG ANALYSIS RESULT")
    print("=" * 60)
    print(rendered)

    assert "calculator.py" in report.file_path
    assert "total" in report.root_cause
    assert report.status == "Bug identified"
    print("  ✓ Traceback Error Log Analysis: PASS")
    return True


def test_traceback_error_log_analysis():
    assert asyncio.run(_async_test_traceback_error_log_analysis())


# ══════════════════════════════════════════════════════════════════════
#  TEST 4: Undetermined Cause Handling
# ══════════════════════════════════════════════════════════════════════
async def _async_test_undetermined_cause_handling():
    analyzer = IssueAnalyzer(project_root=DEMO_ROOT)
    unknown_input = "NameError: name 'non_existent_symbol_12345' is not defined"

    report = await analyzer.analyze(unknown_input)
    rendered = report.render()

    print("\n" + "=" * 60)
    print("TEST 4: UNDETERMINED CAUSE RESULT")
    print("=" * 60)
    print(rendered)

    assert "Root cause could not be determined." in report.root_cause
    assert "Root cause could not be determined." in report.status
    print("  ✓ Undetermined Cause Handling: PASS")
    return True


def test_undetermined_cause_handling():
    assert asyncio.run(_async_test_undetermined_cause_handling())


# ══════════════════════════════════════════════════════════════════════
#  TEST 5: Full Agent Integration
# ══════════════════════════════════════════════════════════════════════
async def _async_test_agent_integration():
    reset_calculator()
    config = AgentConfig(project_root=DEMO_ROOT)
    agent = Agent(config)

    # Test agent.analyze() on bug report
    report1 = await agent.analyze("The divide function is returning the wrong result.")
    assert report1.status == "Bug identified"
    assert "calculator.py" in report1.file_path

    # Test agent.analyze() on error log
    report2 = await agent.analyze("NameError: name 'total' is not defined")
    assert report2.status == "Bug identified"
    assert "calculator.py" in report2.file_path

    # Test agent.run() fallback execution
    result = await agent.run("The divide function is returning the wrong result.")
    assert "STATUS:\nBug identified" in result.summary or "Bug identified" in result.summary
    assert result.success is True

    print("\n" + "=" * 60)
    print("TEST 5: AGENT CLASS INTEGRATION")
    print("=" * 60)
    print("  ✓ agent.analyze() and agent.run() integrated successfully")
    return True


def test_agent_integration():
    assert asyncio.run(_async_test_agent_integration())


# ══════════════════════════════════════════════════════════════════════
#  MAIN RUNNER
# ══════════════════════════════════════════════════════════════════════
async def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   NovaX Agent — Batch 6: Input Understanding & Analysis    ║")
    print("╚════════════════════════════════════════════════════════════╝")

    checks = {
        "Bug Report Analysis": False,
        "Error Log Analysis": False,
        "Traceback Analysis": False,
        "Undetermined Handling": False,
        "Agent Integration": False,
    }

    try:
        checks["Bug Report Analysis"] = await _async_test_bug_report_analysis()
        checks["Error Log Analysis"] = await _async_test_error_log_analysis()
        checks["Traceback Analysis"] = await _async_test_traceback_error_log_analysis()
        checks["Undetermined Handling"] = await _async_test_undetermined_cause_handling()
        checks["Agent Integration"] = await _async_test_agent_integration()
    except Exception as exc:
        print(f"\n❌ Exception during testing: {exc}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("  BATCH 6 TEST SUMMARY")
    print("=" * 60)
    all_passed = True
    for name, passed in checks.items():
        emoji = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:25s} {emoji}")
        if not passed:
            all_passed = False

    print(f"\n  Batch 6 Overall: {'✅ PASS' if all_passed else '❌ FAIL'}\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
