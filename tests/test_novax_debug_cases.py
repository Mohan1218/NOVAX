"""
NovaX Debug Cases — 10 comprehensive end-to-end debugging tests + 1 retry.

Each test case:
  1. Creates an isolated buggy code file + test file
  2. Feeds a bug report to the NovaX IssueAnalyzer
  3. Verifies root cause identification
  4. Applies the fix via CodePatcherTool
  5. Runs the test via TestRunnerTool
  6. Verifies pass/fail based on ACTUAL execution evidence
  7. Cleans up

Additionally includes a RETRY scenario to demonstrate:
  Bug → First fix → Test fails → Analyze failure → Second fix → Test passes
"""

import asyncio
import os
import sys
import shutil
import pytest
import textwrap

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── Make imports work ─────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.agent.analyzer import IssueAnalyzer, InputType
from backend.agent.tools.code_patcher import CodePatcherTool
from backend.agent.tools.test_runner import TestRunnerTool
from backend.agent.tools.code_searcher import CodeSearcherTool
from backend.agent.tools.file_reader import FileReaderTool

# ── Test sandbox directory ────────────────────────────────────────────
SANDBOX = os.path.join(PROJECT_ROOT, "test_sandbox")


def _setup_sandbox():
    """Create a clean sandbox directory."""
    os.makedirs(SANDBOX, exist_ok=True)
    for item in os.listdir(SANDBOX):
        p = os.path.join(SANDBOX, item)
        try:
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
            else:
                os.chmod(p, 0o777)
                os.remove(p)
        except Exception:
            pass


def _teardown_sandbox():
    """Clean the sandbox directory."""
    if os.path.exists(SANDBOX):
        for item in os.listdir(SANDBOX):
            p = os.path.join(SANDBOX, item)
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.chmod(p, 0o777)
                    os.remove(p)
            except Exception:
                pass


def _write(filename: str, content: str):
    """Write content to a file in the sandbox."""
    path = os.path.join(SANDBOX, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 1 — Wrong Operator (+ instead of -)
# ══════════════════════════════════════════════════════════════════════
async def _run_case_1():
    _setup_sandbox()
    _write("calculate.py", """\
        def calculate(a, b):
            return a + b
    """)
    _write("test_calculate.py", """\
        from calculate import calculate

        def test_calculate():
            assert calculate(10, 3) == 7
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "calculate should return the difference between a and b, but it returns the sum."
    )
    print(f"\n[CASE 1] Report:\n{report.render()}")

    assert report.status == "Bug identified", f"Root cause not found: {report.status}"
    assert "calculate" in report.file_path.lower()
    assert "+" in report.root_cause or "addition" in report.root_cause.lower()

    # Apply fix via patch_code
    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="calculate.py",
        mode="replace",
        old_text="return a + b",
        new_text="return a - b",
    )
    assert patch["success"], f"Patch failed: {patch['output']}"

    # Verify fix with tests
    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_calculate.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed after fix: {result['output']}"

    # Verify with run_python
    from backend.agent.tools.python_runner import PythonRunnerTool
    runner = PythonRunnerTool(project_root=SANDBOX)
    verify = await runner.execute(code="from calculate import calculate; print(calculate(10, 3))")
    assert "7" in verify["output"], f"Verification failed: {verify['output']}"

    _teardown_sandbox()
    return True


def test_case_1_wrong_operator():
    assert asyncio.run(_run_case_1())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 2 — Wrong Division Operator (* instead of /)
# ══════════════════════════════════════════════════════════════════════
async def _run_case_2():
    _setup_sandbox()
    _write("divide.py", """\
        def divide(a, b):
            return a * b
    """)
    _write("test_divide.py", """\
        from divide import divide

        def test_divide():
            assert divide(10, 2) == 5
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "The divide function is multiplying instead of dividing."
    )
    print(f"\n[CASE 2] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "divide" in report.file_path.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="divide.py",
        mode="replace",
        old_text="return a * b",
        new_text="return a / b",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_divide.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_2_wrong_division():
    assert asyncio.run(_run_case_2())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 3 — Undefined Variable (total_tax)
# ══════════════════════════════════════════════════════════════════════
async def _run_case_3():
    _setup_sandbox()
    _write("pricing.py", """\
        def calculate_price(price, tax):
            return price + total_tax
    """)
    _write("test_pricing.py", """\
        from pricing import calculate_price

        def test_calculate_price():
            assert calculate_price(100, 10) == 110
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "The calculate_price function crashes because of an undefined variable."
    )
    print(f"\n[CASE 3] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "total_tax" in report.root_cause or "undefined" in report.root_cause.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="pricing.py",
        mode="replace",
        old_text="return price + total_tax",
        new_text="return price + tax",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_pricing.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_3_undefined_variable():
    assert asyncio.run(_run_case_3())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 4 — Wrong Variable Reference (middle_name)
# ══════════════════════════════════════════════════════════════════════
async def _run_case_4():
    _setup_sandbox()
    _write("names.py", """\
        def get_full_name(first_name, last_name):
            return first_name + middle_name + last_name
    """)
    _write("test_names.py", """\
        from names import get_full_name

        def test_get_full_name():
            assert get_full_name("John", "Doe") == "John Doe"
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "get_full_name crashes because it references a variable that is not defined."
    )
    print(f"\n[CASE 4] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "middle_name" in report.root_cause

    # Fix: remove middle_name, add space between first and last
    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="names.py",
        mode="replace",
        old_text='return first_name + middle_name + last_name',
        new_text='return first_name + " " + last_name',
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_names.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_4_wrong_variable_reference():
    assert asyncio.run(_run_case_4())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 5 — Off-by-One Error
# ══════════════════════════════════════════════════════════════════════
async def _run_case_5():
    _setup_sandbox()
    _write("slicer.py", """\
        def get_first_three(numbers):
            return numbers[1:4]
    """)
    _write("test_slicer.py", """\
        from slicer import get_first_three

        def test_get_first_three():
            assert get_first_three([10, 20, 30, 40]) == [10, 20, 30]
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "get_first_three is not returning the first three elements."
    )
    print(f"\n[CASE 5] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "slice" in report.root_cause.lower() or "1" in report.root_cause

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="slicer.py",
        mode="replace",
        old_text="return numbers[1:4]",
        new_text="return numbers[0:3]",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_slicer.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_5_off_by_one():
    assert asyncio.run(_run_case_5())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 6 — Boundary Condition Error (> vs >=)
# ══════════════════════════════════════════════════════════════════════
async def _run_case_6():
    _setup_sandbox()
    _write("adult.py", """\
        def is_adult(age):
            return age > 18
    """)
    _write("test_adult.py", """\
        from adult import is_adult

        def test_is_adult():
            assert is_adult(18) == True
            assert is_adult(17) == False
            assert is_adult(19) == True
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "A person is considered an adult at age 18, but is_adult(18) returns False."
    )
    print(f"\n[CASE 6] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert ">" in report.root_cause or "boundary" in report.root_cause.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="adult.py",
        mode="replace",
        old_text="return age > 18",
        new_text="return age >= 18",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_adult.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_6_boundary_condition():
    assert asyncio.run(_run_case_6())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 7 — Incorrect String Formatting
# ══════════════════════════════════════════════════════════════════════
async def _run_case_7():
    _setup_sandbox()
    _write("greet.py", """\
        def greeting(name):
            return "Hello " + name
    """)
    _write("test_greet.py", """\
        from greet import greeting

        def test_greeting():
            assert greeting("Ganesh") == "Hello, Ganesh!"
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "The greeting format is incorrect. It must contain a comma and exclamation mark."
    )
    print(f"\n[CASE 7] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "format" in report.root_cause.lower() or "Hello" in report.root_cause

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="greet.py",
        mode="replace",
        old_text='return "Hello " + name',
        new_text='return "Hello, " + name + "!"',
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_greet.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_7_string_formatting():
    assert asyncio.run(_run_case_7())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 8 — Zero-Count Guard
# ══════════════════════════════════════════════════════════════════════
async def _run_case_8():
    _setup_sandbox()
    _write("avg.py", """\
        def average(total, count):
            return total / count
    """)
    _write("test_avg.py", """\
        from avg import average

        def test_average_normal():
            assert average(100, 4) == 25

        def test_average_zero():
            assert average(100, 0) == 0
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "If count is 0, average() must return 0 instead of raising ZeroDivisionError."
    )
    print(f"\n[CASE 8] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "zero" in report.root_cause.lower() or "division" in report.root_cause.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="avg.py",
        mode="rewrite",
        new_text="def average(total, count):\n    if count == 0:\n        return 0\n    return total / count\n",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_avg.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_8_zero_count():
    assert asyncio.run(_run_case_8())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 9 — Wrong Return Value
# ══════════════════════════════════════════════════════════════════════
async def _run_case_9():
    _setup_sandbox()
    _write("square.py", """\
        def square(number):
            result = number * number
            return number
    """)
    _write("test_square.py", """\
        from square import square

        def test_square():
            assert square(5) == 25
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "The square function calculates the correct result but returns the original number."
    )
    print(f"\n[CASE 9] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "result" in report.root_cause.lower() or "number" in report.root_cause.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="square.py",
        mode="replace",
        old_text="return number",
        new_text="return result",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_square.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_9_wrong_return():
    assert asyncio.run(_run_case_9())


# ══════════════════════════════════════════════════════════════════════
#  TEST CASE 10 — Percentage Discount
# ══════════════════════════════════════════════════════════════════════
async def _run_case_10():
    _setup_sandbox()
    _write("discount.py", """\
        def calculate_discount(price, discount):
            return price - discount
    """)
    _write("test_discount.py", """\
        from discount import calculate_discount

        def test_calculate_discount():
            assert calculate_discount(1000, 20) == 800
    """)

    analyzer = IssueAnalyzer(project_root=SANDBOX)
    report = await analyzer.analyze(
        "discount is a percentage. calculate_discount should compute the percentage discount."
    )
    print(f"\n[CASE 10] Report:\n{report.render()}")

    assert report.status == "Bug identified"
    assert "percentage" in report.root_cause.lower() or "discount" in report.root_cause.lower()

    patcher = CodePatcherTool(project_root=SANDBOX)
    patch = await patcher.execute(
        path="discount.py",
        mode="replace",
        old_text="return price - discount",
        new_text="return price - (price * discount / 100)",
    )
    assert patch["success"]

    tester = TestRunnerTool(project_root=SANDBOX)
    result = await tester.execute(target="test_discount.py")
    print(f"  Test result: {result['output'][:200]}")
    assert result["success"], f"Tests failed: {result['output']}"

    _teardown_sandbox()
    return True


def test_case_10_percentage_discount():
    assert asyncio.run(_run_case_10())


# ══════════════════════════════════════════════════════════════════════
#  RETRY SCENARIO — First fix fails, second fix succeeds
# ══════════════════════════════════════════════════════════════════════
async def _run_retry_scenario():
    """
    Demonstrates the retry workflow:
      1. Create buggy code (off-by-one in factorial)
      2. Apply a WRONG first fix intentionally
      3. Run tests → observe FAILURE
      4. Analyze failure → apply CORRECT second fix
      5. Run tests → observe PASS
    """
    _setup_sandbox()

    # Buggy code: factorial returns n * n instead of using recursion
    _write("factorial.py", """\
        def factorial(n):
            if n <= 1:
                return 1
            return n * n
    """)
    _write("test_factorial.py", """\
        from factorial import factorial

        def test_factorial_5():
            assert factorial(5) == 120

        def test_factorial_0():
            assert factorial(0) == 1

        def test_factorial_1():
            assert factorial(1) == 1
    """)

    tester = TestRunnerTool(project_root=SANDBOX)
    patcher = CodePatcherTool(project_root=SANDBOX)

    print("\n[RETRY] Step 1: Run tests on buggy code")
    result0 = await tester.execute(target="test_factorial.py")
    print(f"  Tests pass? {result0['success']} (expected: False)")
    assert result0["success"] is False, "Bug should cause test failure"

    # ATTEMPT 1: Apply an INTENTIONALLY WRONG fix (n + n instead of n * factorial(n-1))
    print("\n[RETRY] Step 2: Apply WRONG first fix (return n + n)")
    fix1 = await patcher.execute(
        path="factorial.py",
        mode="replace",
        old_text="return n * n",
        new_text="return n + n",
    )
    assert fix1["success"]

    print("\n[RETRY] Step 3: Run tests after first fix")
    result1 = await tester.execute(target="test_factorial.py")
    print(f"  Tests pass? {result1['success']} (expected: False — wrong fix)")
    print(f"  Output: {result1['output'][:300]}")
    assert result1["success"] is False, "First fix should still fail"

    # ANALYZE FAILURE: The test output shows factorial(5) != 120
    # NovaX would observe the failure and try again
    print("\n[RETRY] Step 4: Analyze failure → factorial(5) returned 10 not 120")
    print("  Diagnosis: The fix 'return n + n' is wrong. Factorial needs recursion.")

    # ATTEMPT 2: Apply CORRECT fix
    print("\n[RETRY] Step 5: Apply CORRECT second fix (return n * factorial(n - 1))")
    fix2 = await patcher.execute(
        path="factorial.py",
        mode="replace",
        old_text="return n + n",
        new_text="return n * factorial(n - 1)",
    )
    assert fix2["success"]

    print("\n[RETRY] Step 6: Run tests after second fix")
    result2 = await tester.execute(target="test_factorial.py")
    print(f"  Tests pass? {result2['success']} (expected: True)")
    print(f"  Output: {result2['output'][:300]}")
    assert result2["success"], f"Second fix should pass: {result2['output']}"

    # Final verification
    from backend.agent.tools.python_runner import PythonRunnerTool
    runner = PythonRunnerTool(project_root=SANDBOX)
    verify = await runner.execute(code="from factorial import factorial; print(factorial(5))")
    assert "120" in verify["output"], f"Verification failed: {verify['output']}"
    print(f"\n[RETRY] Step 7: Verified factorial(5) = 120 ✅")

    _teardown_sandbox()
    return True


def test_retry_scenario():
    assert asyncio.run(_run_retry_scenario())


# ══════════════════════════════════════════════════════════════════════
#  MAIN RUNNER (for standalone execution)
# ══════════════════════════════════════════════════════════════════════
CASE_MAP = {
    "Case 1 — Wrong Operator": _run_case_1,
    "Case 2 — Wrong Division": _run_case_2,
    "Case 3 — Undefined Variable": _run_case_3,
    "Case 4 — Wrong Variable Ref": _run_case_4,
    "Case 5 — Off-by-One": _run_case_5,
    "Case 6 — Boundary Condition": _run_case_6,
    "Case 7 — String Formatting": _run_case_7,
    "Case 8 — Zero Count Guard": _run_case_8,
    "Case 9 — Wrong Return Value": _run_case_9,
    "Case 10 — Percentage Discount": _run_case_10,
    "Retry Scenario": _run_retry_scenario,
}


async def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   NovaX — 10 Debugging Test Cases + Retry Scenario       ║")
    print("╚════════════════════════════════════════════════════════════╝")

    results = {}
    for name, runner in CASE_MAP.items():
        print(f"\n{'━' * 60}")
        print(f"  {name}")
        print(f"{'━' * 60}")
        try:
            passed = await runner()
            results[name] = "PASS" if passed else "FAIL"
        except Exception as exc:
            print(f"  ❌ Exception: {exc}")
            import traceback
            traceback.print_exc()
            results[name] = "FAIL"

    print(f"\n{'═' * 60}")
    print("  FINAL SUMMARY")
    print(f"{'═' * 60}")
    for name, status in results.items():
        emoji = "✅" if status == "PASS" else "❌"
        print(f"  {name:35s} {emoji} {status}")

    passed_count = sum(1 for v in results.values() if v == "PASS")
    failed_count = sum(1 for v in results.values() if v == "FAIL")
    print(f"\n  Passed: {passed_count} / {len(results)}")
    print(f"  Failed: {failed_count} / {len(results)}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
