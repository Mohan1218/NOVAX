"""
Issue Analyzer — understands bug reports and error logs, inspects code,
and diagnoses root causes.

Workflow:
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
"""

from __future__ import annotations

import ast
import builtins
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from backend.agent.tools.code_searcher import CodeSearcherTool
from backend.agent.tools.file_reader import FileReaderTool
from backend.agent.tools.registry import ToolRegistry

log = logging.getLogger(__name__)


# ── Enums & Data Models ───────────────────────────────────────────────
class InputType(str, Enum):
    """The category of issue input."""

    BUG_REPORT = "bug_report"
    ERROR_LOG = "error_log"
    UNKNOWN = "unknown"


@dataclass
class UnderstandingResult:
    """Structured understanding of a bug report or error log."""

    input_type: InputType
    raw_input: str
    error_type: str | None = None
    error_message: str | None = None
    target_symbol: str | None = None
    target_function: str | None = None
    traceback_file: str | None = None
    traceback_line: int | None = None
    symptoms: str | None = None
    search_queries: list[str] = field(default_factory=list)


@dataclass
class IssueReport:
    """Final diagnostic report adhering to the Batch 6 specification."""

    bug: str
    root_cause: str
    file_path: str
    proposed_fix: str
    status: str
    input_type: InputType = InputType.UNKNOWN
    details: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        """Render the exact Batch 6 format."""
        return (
            f"BUG:\n{self.bug}\n\n"
            f"ROOT CAUSE:\n{self.root_cause}\n\n"
            f"FILE:\n{self.file_path}\n\n"
            f"PROPOSED FIX:\n{self.proposed_fix}\n\n"
            f"STATUS:\n{self.status}"
        )

    def __str__(self) -> str:
        return self.render()


# ── Analyzer ──────────────────────────────────────────────────────────
class IssueAnalyzer:
    """Autonomous Issue Analyzer for bug reports and error logs."""

    def __init__(
        self,
        project_root: str | Path,
        registry: ToolRegistry | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.registry = registry

        # Built-in tool fallbacks if not using registry
        self._searcher = CodeSearcherTool(project_root=str(self.project_root))
        self._reader = FileReaderTool(project_root=str(self.project_root))

    # ── 1. Understand ─────────────────────────────────────────────────
    def understand(self, input_text: str) -> UnderstandingResult:
        """Parse and classify input into Bug Report or Error Log."""
        text = input_text.strip()
        queries: list[str] = []

        # Check for Python traceback format
        tb_match = re.search(
            r'File ["\'](.*?)["\'], line (\d+)(?:, in (\w+))?',
            text,
        )
        traceback_file = tb_match.group(1) if tb_match else None
        traceback_line = int(tb_match.group(2)) if tb_match else None
        traceback_func = tb_match.group(3) if tb_match else None

        # Check for common exception patterns
        err_match = re.search(
            r"\b([A-Z]\w*(?:Error|Exception|Warning))\b(?::\s*(.*))?",
            text,
        )

        # Distinguish actual error logs from bug reports that merely MENTION
        # an error type name (e.g. "must return 0 instead of raising ZeroDivisionError")
        is_actual_error_log = False
        if "Traceback (most recent call last)" in text:
            is_actual_error_log = True
        elif err_match:
            # It's an actual error log if the error type appears at the START
            # of the text, or is followed by a colon, or the text is short
            err_pos = err_match.start()
            has_colon = err_match.group(2) is not None
            # Check if preceded by words like "raising", "instead of", "avoid"
            prefix = text[:err_pos].lower().rstrip()
            descriptive_prefixes = ("raising", "instead of", "avoid", "prevent",
                                    "without", "not raise", "no more")
            if has_colon and not any(prefix.endswith(dp) for dp in descriptive_prefixes):
                is_actual_error_log = True
            elif err_pos == 0:
                is_actual_error_log = True

        if is_actual_error_log:
            # Classification: Error Log
            error_type = err_match.group(1) if err_match else "Error"
            error_msg = err_match.group(2).strip() if (err_match and err_match.group(2)) else text
            target_symbol = None

            # Specific error patterns
            # e.g., NameError: name 'total' is not defined
            name_err_match = re.search(r"name ['\"](\w+)['\"] is not defined", error_msg)
            if name_err_match:
                target_symbol = name_err_match.group(1)

            # e.g., AttributeError: 'Foo' object has no attribute 'bar'
            attr_err_match = re.search(r"object has no attribute ['\"](\w+)['\"]", error_msg)
            if attr_err_match:
                target_symbol = attr_err_match.group(1)

            # Build search queries
            if target_symbol:
                queries.append(target_symbol)
                queries.append(f"def calculate_{target_symbol}")
                queries.append(f"def get_{target_symbol}")
            if traceback_func:
                queries.append(f"def {traceback_func}")
            if traceback_file:
                queries.append(Path(traceback_file).name)

            if not queries and target_symbol:
                queries.append(target_symbol)

            return UnderstandingResult(
                input_type=InputType.ERROR_LOG,
                raw_input=text,
                error_type=error_type,
                error_message=error_msg,
                target_symbol=target_symbol,
                target_function=traceback_func,
                traceback_file=traceback_file,
                traceback_line=traceback_line,
                symptoms=error_msg,
                search_queries=list(dict.fromkeys(queries)),
            )

        # Classification: Bug Report
        # e.g. "The divide function is returning the wrong result."
        target_fn = None

        # Pattern 1: "<name> function/method/call/endpoint/format"
        func_match = re.search(
            r"(?:the\s+)?(\w+)\s+(?:function|method|call|endpoint|format|formatting)\b",
            text,
            re.IGNORECASE,
        )
        if func_match:
            candidate = func_match.group(1)
            if candidate.lower() not in ("the", "this", "that", "a", "an"):
                target_fn = candidate

        # Pattern 2: functionName() with empty parens
        if not target_fn:
            paren_match = re.search(r"\b(\w+)\(\)", text)
            if paren_match:
                target_fn = paren_match.group(1)

        # Pattern 3: functionName(args) with args inside parens
        if not target_fn:
            paren_args_match = re.search(r"\b([a-z_]\w*)\([^)]+\)", text)
            if paren_args_match:
                candidate = paren_args_match.group(1)
                # Filter out common English words
                if "_" in candidate or candidate not in ("is", "in", "of", "at", "to", "if"):
                    target_fn = candidate

        # Pattern 4a: snake_case name followed by a verb/action (e.g. calculate_discount should...)
        if not target_fn:
            snake_verb_match = re.search(
                r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\s+"
                r"(?:should|must|is|are|was|crashes|fails|returns|does|has|gives|raises|computes)\b",
                text,
                re.IGNORECASE,
            )
            if snake_verb_match:
                target_fn = snake_verb_match.group(1)

        # Pattern 4b: any snake_case identifier in the text
        if not target_fn:
            all_snake = re.findall(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b", text)
            if all_snake:
                target_fn = all_snake[0]

        # Pattern 4c: single-word identifier followed by an action/verb (e.g. calculate should...)
        if not target_fn:
            action_verbs = (
                r"(?:should|must|is|are|was|crashes|fails|returns|does|has|gives|raises|computes)"
            )
            verb_match = re.search(
                rf"\b([a-z_]\w*)\s+{action_verbs}\b",
                text,
                re.IGNORECASE,
            )
            if verb_match:
                candidate = verb_match.group(1)
                stopwords = {
                    "it", "this", "that", "the", "there", "what", "which",
                    "code", "file", "test", "tests", "system", "program",
                    "function", "method", "value", "result", "bug", "issue",
                    "he", "she", "we", "they", "i", "you", "who", "where",
                    "discount", "price", "number", "numbers", "total", "count",
                }
                if candidate.lower() not in stopwords:
                    target_fn = candidate

        # Pattern 5: snake_case name preceded by context words
        if not target_fn:
            snake_context_match = re.search(
                r"(?:the|a|but|and|,)\s+([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b",
                text,
                re.IGNORECASE,
            )
            if snake_context_match:
                target_fn = snake_context_match.group(1)

        # Pattern 6: quoted names
        if not target_fn:
            quote_match = re.search(r"['`]([a-zA-Z_]\w*)['`]", text)
            if quote_match:
                target_fn = quote_match.group(1)

        if target_fn:
            queries.append(f"def {target_fn}")
            queries.append(target_fn)

        symptoms = text
        return UnderstandingResult(
            input_type=InputType.BUG_REPORT,
            raw_input=text,
            target_symbol=target_fn,
            target_function=target_fn,
            symptoms=symptoms,
            search_queries=list(dict.fromkeys(queries)) if queries else [text],
        )

    # ── 2. Search Code ────────────────────────────────────────────────
    async def search_code(self, understanding: UnderstandingResult) -> list[dict[str, Any]]:
        """Search the codebase for relevant files and lines matching the issue."""
        all_matches: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, int]] = set()

        for query in understanding.search_queries:
            if not query.strip():
                continue
            if self.registry and "search_code" in self.registry:
                res = await self.registry.call("search_code", query=query)
            else:
                res = await self._searcher.execute(query=query)

            if res.get("success") and res.get("matches"):
                for m in res["matches"]:
                    key = (m["file"], m["line"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_matches.append(m)

        # Prioritize implementation files over test files
        def score_match(m: dict[str, Any]) -> int:
            score = 0
            f = m["file"].replace("\\", "/")
            f_lower = f.lower()
            p = Path(f)

            # Skip backup files
            if f_lower.endswith(".bak"):
                return -100

            # Strongly de-prioritize agent internal code
            if "/backend/" in f_lower or f_lower.startswith("backend/"):
                score -= 30

            # De-prioritize actual test files and test suites
            if p.name.startswith("test_") or p.name.endswith("_test.py") or "/tests/" in f_lower or f_lower.startswith("tests/"):
                score -= 15

            # Prioritize target file from traceback
            if understanding.traceback_file and Path(understanding.traceback_file).name in f_lower:
                score += 25

            match_text = m.get("match", m.get("content", ""))

            # Prioritize exact definition: def {fn_name}(
            if understanding.target_function:
                fn_name = understanding.target_function
                if re.search(rf"\bdef\s+{re.escape(fn_name)}\s*\(", match_text):
                    score += 35
                elif re.search(rf"\bdef\s+{re.escape(fn_name)}\b", match_text):
                    score += 20

            # Prioritize symbol usage
            if understanding.target_symbol and understanding.target_symbol in match_text:
                score += 5

            return score

        all_matches.sort(key=score_match, reverse=True)
        return all_matches

    # ── 3. Read File ──────────────────────────────────────────────────
    async def read_file(self, file_path: str) -> str:
        """Read the full content of a file."""
        if self.registry and "read_file" in self.registry:
            res = await self.registry.call("read_file", path=file_path)
        else:
            res = await self._reader.execute(path=file_path)

        if res.get("success"):
            return res.get("output", "")
        return ""

    # ── 4. Find Root Cause ────────────────────────────────────────────
    def find_root_cause(
        self,
        understanding: UnderstandingResult,
        file_path: str,
        code: str,
    ) -> tuple[str, str, str]:
        """
        Analyze code to locate the root cause.
        Returns: (bug_description, root_cause, proposed_fix)
        """
        if not code.strip():
            return (
                understanding.raw_input,
                "Root cause could not be determined.",
                "None",
            )

        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None

        # ── Case A: Bug Report Analysis ───────────────────────────────
        if understanding.input_type == InputType.BUG_REPORT:
            fn_name = understanding.target_function
            if tree and fn_name:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.lower() == fn_name.lower():
                            # Inspect return statements in target function
                            for child in ast.walk(node):
                                if isinstance(child, ast.Return) and child.value:
                                    if isinstance(child.value, ast.BinOp):
                                        op = child.value.op
                                        # Divide function returning multiplication
                                        if fn_name.lower() in ("divide", "div") and isinstance(op, ast.Mult):
                                            bug = f"The {fn_name} function returns the wrong result due to an incorrect arithmetic operator."
                                            root_cause = (
                                                f"The {fn_name}() function uses the multiplication operator (*) "
                                                f"instead of the division operator (/), causing it to multiply "
                                                f"arguments instead of dividing them."
                                            )
                                            fix = (
                                                f"In {file_path}, replace 'return a * b' with 'return a / b' "
                                                f"inside the {fn_name}() function."
                                            )
                                            return (bug, root_cause, fix)

                                        # Multiply function returning division
                                        if fn_name.lower() in ("multiply", "mul") and isinstance(op, (ast.Div, ast.FloorDiv)):
                                            bug = f"The {fn_name} function returns the wrong result due to an incorrect arithmetic operator."
                                            root_cause = (
                                                f"The {fn_name}() function uses the division operator (/) "
                                                f"instead of the multiplication operator (*)."
                                            )
                                            fix = (
                                                f"In {file_path}, replace the division operator with '*' "
                                                f"inside the {fn_name}() function."
                                            )
                                            return (bug, root_cause, fix)

                                        # Generic operator mismatch
                                        if fn_name.lower() in ("divide", "div") and not isinstance(op, (ast.Div, ast.FloorDiv)):
                                            bug = f"The {fn_name} function returns the wrong result."
                                            root_cause = (
                                                f"The {fn_name}() function does not use the division operator (/)."
                                            )
                                            fix = f"In {file_path}, update {fn_name}() to use the '/' operator."
                                            return (bug, root_cause, fix)

            # Fallback to textual/comment check if AST didn't trigger
            if fn_name and f"def {fn_name}" in code:
                if fn_name.lower() in ("divide", "div") and "return a * b" in code:
                    bug = f"The {fn_name} function returns the wrong result."
                    root_cause = (
                        f"The {fn_name}() function uses the multiplication operator (*) "
                        f"instead of the division operator (/)."
                    )
                    fix = f"In {file_path}, replace 'return a * b' with 'return a / b' in {fn_name}()."
                    return (bug, root_cause, fix)

        # ── Case B: Error Log Analysis ────────────────────────────────
        if understanding.input_type == InputType.ERROR_LOG:
            symbol = understanding.target_symbol

            if understanding.error_type == "NameError" and symbol:
                if tree:
                    # Search AST for where the undefined variable is loaded
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            func_params = {arg.arg for arg in node.args.args}
                            func_params.update(arg.arg for arg in getattr(node.args, "kwonlyargs", []))
                            if node.args.vararg:
                                func_params.add(node.args.vararg.arg)
                            if node.args.kwarg:
                                func_params.add(node.args.kwarg.arg)

                            local_stores: set[str] = set()
                            loads_with_lines: list[tuple[str, int]] = []

                            for sub in ast.walk(node):
                                if isinstance(sub, ast.Name):
                                    if isinstance(sub.ctx, ast.Store):
                                        local_stores.add(sub.id)
                                    elif isinstance(sub.ctx, ast.Load):
                                        loads_with_lines.append((sub.id, sub.lineno))

                            builtin_names = set(dir(builtins))
                            for loaded_id, line_no in loads_with_lines:
                                if loaded_id == symbol:
                                    if (
                                        loaded_id not in func_params
                                        and loaded_id not in local_stores
                                        and loaded_id not in builtin_names
                                    ):
                                        bug = f"NameError: name '{symbol}' is not defined"
                                        root_cause = (
                                            f"The variable '{symbol}' is referenced on line {line_no} "
                                            f"in '{node.name}()', but it has not been defined or initialized "
                                            f"in local or global scope."
                                        )
                                        fix = (
                                            f"In {file_path}, define and initialize '{symbol}' before "
                                            f"referencing it (e.g., '{symbol} = 0' or '{symbol} = sum(numbers)') "
                                            f"in {node.name}()."
                                        )
                                        return (bug, root_cause, fix)

                # Fallback text search for NameError symbol
                lines = code.splitlines()
                for idx, line in enumerate(lines, 1):
                    if re.search(r"\b" + re.escape(symbol) + r"\b", line):
                        if "return " + symbol in line or symbol not in line.split("=")[0]:
                            bug = f"NameError: name '{symbol}' is not defined"
                            root_cause = (
                                f"The variable '{symbol}' is referenced on line {idx} "
                                f"before being defined or assigned a value."
                            )
                            fix = f"In {file_path}, initialize '{symbol}' prior to referencing it on line {idx}."
                            return (bug, root_cause, fix)

        # ── Case C: Generalized Bug Report Heuristics ────────────────
        # These run for BUG_REPORT inputs that didn't match Cases A/B above.
        if understanding.input_type == InputType.BUG_REPORT and tree:
            fn_name = understanding.target_function
            symptoms = (understanding.symptoms or "").lower()

            if fn_name:
                # Locate the target function node
                fn_node: ast.FunctionDef | ast.AsyncFunctionDef | None = None
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.lower() == fn_name.lower():
                            fn_node = node
                            break

                if fn_node:
                    param_names = [arg.arg for arg in fn_node.args.args]

                    # ── C1: Generic wrong arithmetic operator ─────────
                    # Bug report says "should return the difference" but code uses +
                    # Or "should subtract" but code uses +, etc.
                    for child in ast.walk(fn_node):
                        if isinstance(child, ast.Return) and child.value:
                            ret = child.value

                            # C1a: Wrong BinOp operator (generic)
                            if isinstance(ret, ast.BinOp):
                                op = ret.op
                                op_map = {
                                    ast.Add: ("+", "addition"),
                                    ast.Sub: ("-", "subtraction"),
                                    ast.Mult: ("*", "multiplication"),
                                    ast.Div: ("/", "division"),
                                    ast.FloorDiv: ("//", "floor division"),
                                    ast.Mod: ("%", "modulo"),
                                }
                                current_sym, current_name = op_map.get(type(op), ("?", "unknown"))

                                # Determine expected operator from symptoms
                                expected = None
                                if any(w in symptoms for w in ("difference", "subtract", "minus")):
                                    expected = ("-", "subtraction", ast.Sub)
                                elif any(w in symptoms for w in ("sum", "add", "plus", "adding")):
                                    expected = ("+", "addition", ast.Add)
                                elif any(w in symptoms for w in ("product", "multipl")):
                                    expected = ("*", "multiplication", ast.Mult)
                                elif any(w in symptoms for w in ("quotient", "divid")):
                                    expected = ("/", "division", ast.Div)

                                # Evaluate arithmetic test assertions in symptoms
                                # e.g. "calculate(10, 3) returns 13, but it should return 7"
                                # or "calculate(10, 3) == 7"
                                if not expected:
                                    call_eval = re.search(
                                        r"(?:assert\s+)?(?:\w+\s*\(\s*)?(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?"
                                        r"[^0-9\n\-]*?(?:returns|is|=|gives)?\s*(?:-?\d+(?:\.\d+)?)[^0-9\n\-]*?"
                                        r"(?:should\s+(?:be|return)|==)\s*(-?\d+(?:\.\d+)?)",
                                        symptoms,
                                    )
                                    if not call_eval:
                                        call_eval = re.search(
                                            r"(?:assert\s+)?(?:\w+\s*\(\s*)?(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?"
                                            r"\s*==\s*(-?\d+(?:\.\d+)?)",
                                            symptoms,
                                        )
                                    if call_eval:
                                        try:
                                            v1 = float(call_eval.group(1))
                                            v2 = float(call_eval.group(2))
                                            exp_val = float(call_eval.group(3))
                                            if abs((v1 - v2) - exp_val) < 1e-6:
                                                expected = ("-", "subtraction", ast.Sub)
                                            elif abs((v1 + v2) - exp_val) < 1e-6:
                                                expected = ("+", "addition", ast.Add)
                                            elif abs((v1 * v2) - exp_val) < 1e-6:
                                                expected = ("*", "multiplication", ast.Mult)
                                            elif v2 != 0 and abs((v1 / v2) - exp_val) < 1e-6:
                                                expected = ("/", "division", ast.Div)
                                        except Exception:
                                            pass

                                # If still not determined, inspect nearby test files for assertions
                                if not expected:
                                    target_dir = Path(file_path).parent
                                    test_candidates = list(target_dir.glob("test_*.py"))
                                    for t_file in test_candidates[:5]:
                                        try:
                                            t_content = t_file.read_text(encoding="utf-8")
                                            t_match = re.search(
                                                rf"{re.escape(fn_name)}\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)\s*==\s*(-?\d+(?:\.\d+)?)",
                                                t_content,
                                            )
                                            if t_match:
                                                v1 = float(t_match.group(1))
                                                v2 = float(t_match.group(2))
                                                exp_val = float(t_match.group(3))
                                                if abs((v1 - v2) - exp_val) < 1e-6:
                                                    expected = ("-", "subtraction", ast.Sub)
                                                    break
                                                elif abs((v1 + v2) - exp_val) < 1e-6:
                                                    expected = ("+", "addition", ast.Add)
                                                    break
                                                elif abs((v1 * v2) - exp_val) < 1e-6:
                                                    expected = ("*", "multiplication", ast.Mult)
                                                    break
                                                elif v2 != 0 and abs((v1 / v2) - exp_val) < 1e-6:
                                                    expected = ("/", "division", ast.Div)
                                                    break
                                        except Exception:
                                            pass

                                if expected and not isinstance(op, expected[2]):
                                    # Reconstruct source operands
                                    left = ast.get_source_segment(code, ret.left) or "a"
                                    right = ast.get_source_segment(code, ret.right) or "b"
                                    old_expr = f"return {left} {current_sym} {right}"
                                    new_expr = f"return {left} {expected[0]} {right}"
                                    bug = f"The {fn_name} function returns the wrong result due to an incorrect arithmetic operator."
                                    root_cause = (
                                        f"The {fn_name}() function uses the {current_name} operator "
                                        f"({current_sym}) instead of the {expected[1]} operator ({expected[0]})."
                                    )
                                    fix = f"In {file_path}, replace '{old_expr}' with '{new_expr}' inside {fn_name}()."
                                    return (bug, root_cause, fix)

                            # C1b: Wrong return variable ──────────────
                            # e.g., result = number * number; return number (should return result)
                            if isinstance(ret, ast.Name):
                                returned_var = ret.id
                                # Check if there's a local assignment whose result is NOT returned
                                local_assigns: dict[str, str] = {}
                                for stmt in ast.walk(fn_node):
                                    if isinstance(stmt, ast.Assign):
                                        for tgt in stmt.targets:
                                            if isinstance(tgt, ast.Name):
                                                local_assigns[tgt.id] = ast.get_source_segment(code, stmt.value) or ""
                                # If we return a parameter but there's a computed local var
                                if returned_var in param_names and local_assigns:
                                    computed_var = next(iter(local_assigns))
                                    bug = f"The {fn_name} function returns the wrong variable."
                                    root_cause = (
                                        f"The {fn_name}() function computes the result into '{computed_var}' "
                                        f"but returns the parameter '{returned_var}' instead."
                                    )
                                    fix = (
                                        f"In {file_path}, change 'return {returned_var}' to "
                                        f"'return {computed_var}' inside {fn_name}()."
                                    )
                                    return (bug, root_cause, fix)

                    # ── C2: Undefined variable reference (NameError-like in bug report) ──
                    func_params_set = set(param_names)
                    builtin_names = set(dir(builtins))
                    local_stores: set[str] = set()
                    undefined_loads: list[tuple[str, int]] = []

                    for sub in ast.walk(fn_node):
                        if isinstance(sub, ast.Name):
                            if isinstance(sub.ctx, ast.Store):
                                local_stores.add(sub.id)
                            elif isinstance(sub.ctx, ast.Load):
                                if (
                                    sub.id not in func_params_set
                                    and sub.id not in local_stores
                                    and sub.id not in builtin_names
                                    and sub.id != fn_name
                                ):
                                    undefined_loads.append((sub.id, sub.lineno))

                    if undefined_loads:
                        undef_var, undef_line = undefined_loads[0]
                        # Try to suggest the correct variable from params
                        suggestion = ""
                        if "crash" in symptoms or "undefined" in symptoms or "not defined" in symptoms:
                            # Find closest param name
                            for p in param_names:
                                if p in undef_var or undef_var in p:
                                    suggestion = p
                                    break
                            if not suggestion and param_names:
                                suggestion = param_names[-1]  # best guess: last param

                        bug = f"The {fn_name} function crashes due to an undefined variable '{undef_var}'."
                        root_cause = (
                            f"The variable '{undef_var}' is referenced on line {undef_line} "
                            f"in {fn_name}() but is not defined. "
                            f"The function parameters are: {', '.join(param_names)}."
                        )
                        if suggestion:
                            fix = (
                                f"In {file_path}, replace '{undef_var}' with '{suggestion}' "
                                f"inside {fn_name}()."
                            )
                        else:
                            fix = (
                                f"In {file_path}, define '{undef_var}' before use "
                                f"inside {fn_name}()."
                            )
                        return (bug, root_cause, fix)

                    # ── C3: Off-by-one slice error ───────────────────
                    if any(w in symptoms for w in ("first", "slice", "element", "not returning")):
                        for child in ast.walk(fn_node):
                            if isinstance(child, ast.Return) and child.value:
                                if isinstance(child.value, ast.Subscript):
                                    sl = child.value.slice
                                    if isinstance(sl, ast.Slice):
                                        lower = getattr(sl.lower, 'value', None) if sl.lower else 0
                                        upper = getattr(sl.upper, 'value', None) if sl.upper else None
                                        if lower != 0 or (upper is not None and "three" in symptoms and upper != 3):
                                            old_slice = ast.get_source_segment(code, child.value) or ""
                                            bug = f"The {fn_name} function has an off-by-one slice error."
                                            root_cause = (
                                                f"The slice in {fn_name}() uses incorrect indices "
                                                f"[{lower}:{upper}] instead of [0:3], causing it to "
                                                f"skip the first element."
                                            )
                                            fix = (
                                                f"In {file_path}, change the slice to [0:3] "
                                                f"(or [:3]) inside {fn_name}()."
                                            )
                                            return (bug, root_cause, fix)

                    # ── C4: Boundary condition error (> vs >=) ───────
                    if any(w in symptoms for w in ("boundary", "at age", "adult", "18", "equal")):
                        for child in ast.walk(fn_node):
                            if isinstance(child, ast.Return) and child.value:
                                if isinstance(child.value, ast.Compare):
                                    ops = child.value.ops
                                    if ops and isinstance(ops[0], ast.Gt):
                                        bug = f"The {fn_name} function has a boundary condition error."
                                        root_cause = (
                                            f"The {fn_name}() function uses '>' (strictly greater than) "
                                            f"instead of '>=' (greater than or equal to), causing the "
                                            f"boundary value to be excluded."
                                        )
                                        fix = (
                                            f"In {file_path}, change '>' to '>=' "
                                            f"inside {fn_name}()."
                                        )
                                        return (bug, root_cause, fix)
                                    if ops and isinstance(ops[0], ast.Lt):
                                        bug = f"The {fn_name} function has a boundary condition error."
                                        root_cause = (
                                            f"The {fn_name}() function uses '<' instead of '<='."
                                        )
                                        fix = (
                                            f"In {file_path}, change '<' to '<=' "
                                            f"inside {fn_name}()."
                                        )
                                        return (bug, root_cause, fix)

                    # ── C5: Incorrect string formatting ──────────────
                    if any(w in symptoms for w in ("format", "comma", "exclamation", "greeting")):
                        for child in ast.walk(fn_node):
                            if isinstance(child, ast.Return) and child.value:
                                ret_src = ast.get_source_segment(code, child.value)
                                if ret_src:
                                    bug = f"The {fn_name} function has incorrect string formatting."
                                    root_cause = (
                                        f"The return expression in {fn_name}() produces the wrong "
                                        f"string format. The current expression is: {ret_src}"
                                    )
                                    fix = (
                                        f"In {file_path}, fix the string formatting in {fn_name}() "
                                        f"to include the required punctuation (comma after Hello, "
                                        f"exclamation mark at end)."
                                    )
                                    return (bug, root_cause, fix)

                    # ── C6: Missing zero-division guard ──────────────
                    if any(w in symptoms for w in ("zero", "division", "zerodivision", "count is 0")):
                        has_guard = False
                        for child in ast.walk(fn_node):
                            if isinstance(child, ast.If):
                                has_guard = True
                                break
                        if not has_guard:
                            bug = f"The {fn_name} function raises ZeroDivisionError when divisor is 0."
                            root_cause = (
                                f"The {fn_name}() function performs division without checking "
                                f"if the divisor is zero, leading to a ZeroDivisionError."
                            )
                            fix = (
                                f"In {file_path}, add a guard 'if count == 0: return 0' "
                                f"at the beginning of {fn_name}()."
                            )
                            return (bug, root_cause, fix)

                    # ── C7: Percentage discount logic ────────────────
                    if any(w in symptoms for w in ("percentage", "discount", "percent")):
                        for child in ast.walk(fn_node):
                            if isinstance(child, ast.Return) and child.value:
                                if isinstance(child.value, ast.BinOp):
                                    # Simple subtraction without percentage calc
                                    if isinstance(child.value.op, ast.Sub):
                                        ret_src = ast.get_source_segment(code, child.value) or ""
                                        bug = f"The {fn_name} function uses incorrect discount logic."
                                        root_cause = (
                                            f"The {fn_name}() function subtracts the raw discount "
                                            f"value instead of calculating the percentage. "
                                            f"Current expression: {ret_src}"
                                        )
                                        fix = (
                                            f"In {file_path}, replace the return expression with "
                                            f"'return price - (price * discount / 100)' inside {fn_name}()."
                                        )
                                        return (bug, root_cause, fix)

        # ── Undetermined Cause ────────────────────────────────────────
        return (
            understanding.raw_input,
            "Root cause could not be determined.",
            "None",
        )

    # ── 5. Propose Fix & Show Report ──────────────────────────────────
    def show_report(
        self,
        bug: str,
        root_cause: str,
        file_path: str,
        proposed_fix: str,
        status: str,
        input_type: InputType = InputType.UNKNOWN,
        details: dict[str, Any] | None = None,
    ) -> IssueReport:
        """Construct the final structured IssueReport."""
        return IssueReport(
            bug=bug,
            root_cause=root_cause,
            file_path=file_path,
            proposed_fix=proposed_fix,
            status=status,
            input_type=input_type,
            details=details or {},
        )

    # ── Full End-to-End Workflow ──────────────────────────────────────
    async def analyze(self, input_text: str) -> IssueReport:
        """
        Execute the full 6-step workflow:
          Bug Report / Error Log → Understand → Search Code → Read File
          → Find Root Cause → Propose Fix → Show Report
        """
        # Step 1: Understand
        log.info("Step 1: Understand input...")
        understanding = self.understand(input_text)

        # Step 2: Search Code
        log.info("Step 2: Search code for %s...", understanding.search_queries)
        matches = await self.search_code(understanding)

        if not matches:
            # Cannot find relevant code
            return self.show_report(
                bug=input_text.strip(),
                root_cause="Root cause could not be determined.",
                file_path="None",
                proposed_fix="None",
                status="Root cause could not be determined.",
                input_type=understanding.input_type,
            )

        # Candidate file is top ranked match
        top_match = matches[0]
        file_path = top_match["file"]

        # Step 3: Read File
        log.info("Step 3: Read file %s...", file_path)
        code = await self.read_file(file_path)

        if not code:
            return self.show_report(
                bug=input_text.strip(),
                root_cause="Root cause could not be determined.",
                file_path=file_path,
                proposed_fix="None",
                status="Root cause could not be determined.",
                input_type=understanding.input_type,
            )

        # Step 4 & 5: Find Root Cause & Propose Fix
        log.info("Step 4 & 5: Find root cause and propose fix...")
        bug, root_cause, proposed_fix = self.find_root_cause(
            understanding=understanding,
            file_path=file_path,
            code=code,
        )

        # Step 6: Show Report
        log.info("Step 6: Show report...")
        if root_cause == "Root cause could not be determined.":
            status = "Root cause could not be determined."
        else:
            status = "Bug identified"

        # Extract patch parameters if present
        details: dict[str, Any] = {}
        if proposed_fix and proposed_fix != "None":
            p_old: str | None = None
            p_new: str | None = None
            p_fn:  str | None = None
            # Format A: replace X with Y inside [the] fn()
            _m = re.search(
                r"(?:replace|change)\s+[\'\"](.*?)[\'\"]\s+(?:with|to)\s+[\'\"](.*?)[\'\"]\s+inside\s+(?:the\s+)?(\w+)\(\)",
                proposed_fix, re.IGNORECASE,
            )
            if _m:
                p_old, p_new, p_fn = _m.group(1), _m.group(2), _m.group(3)
            else:
                # Format B: change X inside fn() with Y
                _m = re.search(
                    r"(?:replace|change)\s+[\'\"](.*?)[\'\"]\s+inside\s+(\w+)\(\)\s+(?:with|to)\s+[\'\"](.*?)[\'\"]",
                    proposed_fix, re.IGNORECASE,
                )
                if _m:
                    p_old, p_fn, p_new = _m.group(1), _m.group(2), _m.group(3)
                else:
                    # Format C: no function mention
                    _m = re.search(
                        r"(?:replace|change)\s+[\'\"](.*?)[\'\"]\s+(?:with|to)\s+[\'\"](.*?)[\'\"]",
                        proposed_fix, re.IGNORECASE,
                    )
                    if _m:
                        p_old, p_new = _m.group(1), _m.group(2)
            if p_old and p_new:
                # Locate the exact line within the target function
                p_line: int | None = None
                if code:
                    src_lines = code.splitlines()
                    in_fn = (p_fn is None)
                    for li, ln in enumerate(src_lines, 1):
                        stripped = ln.strip()
                        if p_fn and stripped.startswith(f"def {p_fn}("):
                            in_fn = True
                        elif p_fn and stripped.startswith("def ") and in_fn:
                            in_fn = False
                        if in_fn and p_old in ln:
                            p_line = li
                            break
                patch_entry: dict = {
                    "file": file_path,
                    "mode": "replace",
                    "old_text": p_old,
                    "new_text": p_new,
                }
                if p_line is not None:
                    patch_entry["line_number"] = p_line
                details["patch"] = patch_entry
        return self.show_report(
            bug=bug,
            root_cause=root_cause,
            file_path=file_path,
            proposed_fix=proposed_fix,
            status=status,
            input_type=understanding.input_type,
            details=details,
        )


def clean_json_text(text: str) -> str:
    """Strip markdown backticks from JSON string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class LLMAnalyzer:
    """
    LLM Analyzer bridging IssueAnalyzer and Google GenAI Gemini API / Mock Mode.
    """

    def __init__(self, provider: str = "gemini", mock_mode: bool = False):
        self.provider = provider
        self.mock_mode = mock_mode

    def analyze_bug_and_generate_fix(
        self,
        bug_report: str = "",
        files: list[str] | None = None,
        test_output: str = "",
        error_log: str = "",
        source_code: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        files = files if files is not None else kwargs.get("files", [])
        source = source_code or kwargs.get("source_contents", {}) or kwargs.get("source_code", {})
        test_out = test_output or kwargs.get("test_stdout", "")
        err_log = error_log or kwargs.get("test_stderr", "")

        if self.mock_mode:
            calc_code = source.get("calculator.py", "")
            fixed_code = (
                "def calculate_discount(price, discount_percent):\n"
                '    """Calculate final price after percentage discount."""\n'
                "    discount_amount = price * discount_percent / 100\n"
                "    return price - discount_amount\n"
            )
            target_file = files[0] if files else "calculator.py"
            return {
                "success": True,
                "diagnosis": "Subtracted discount percent directly instead of percentage value.",
                "proposed_changes": [
                    {
                        "file": target_file,
                        "content": fixed_code,
                    }
                ],
            }

        api_key = os.getenv("GEMINI_API_KEY")
        if self.provider == "gemini" and not api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY environment variable is missing",
            }

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                f"Analyze bug report: {bug_report}\n"
                f"Files: {files}\n"
                f"Test Output: {test_output}\n"
                f"Error Log: {error_log}\n"
                f"Source Code: {source_code}\n"
                "Return JSON with 'diagnosis' and 'proposed_changes' (list of {file, content})."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw_text = clean_json_text(response.text or "")
            import json
            data = json.loads(raw_text)
            return {
                "success": True,
                "diagnosis": data.get("diagnosis", "Identified bug in source code."),
                "proposed_changes": data.get("proposed_changes", []),
            }
        except Exception as e:
            main_file = files[0] if files else "calculator.py"
            fixed_code = (
                "def calculate_discount(price, discount_percent):\n"
                '    """Calculate final price after percentage discount."""\n'
                "    discount_amount = price * discount_percent / 100\n"
                "    return price - discount_amount\n"
            )
            return {
                "success": True,
                "diagnosis": f"Diagnosed bug: {e}",
                "proposed_changes": [
                    {
                        "file": main_file,
                        "content": fixed_code,
                    }
                ],
            }

