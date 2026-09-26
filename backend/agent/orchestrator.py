import time
from typing import Dict, Any, Optional, List
from backend.services.agent_interface import AgentBackendInterface
from backend.agent.analyzer import LLMAnalyzer
from backend.agent.tester_agent import TesterAgent
from backend.agent.coder_agent import CoderAgent

MAX_RETRIES = 3


class AutonomousDebuggerAgent:
    """
    Autonomous BugHunter AI Agent Orchestrator.
    Executes a real tool-using debug workflow driven by an LLM state machine.
    Must operate ONLY through AgentBackendInterface.
    """

    def __init__(self, interface: Optional[AgentBackendInterface] = None, analyzer: Optional[LLMAnalyzer] = None):
        self.interface = interface or AgentBackendInterface()
        self.analyzer = analyzer or LLMAnalyzer()
        self.tester = TesterAgent(self.interface)
        self.coder = CoderAgent(self.interface)

    def run_debug_job(self, job_id: str, workspace: str, bug_report: str) -> Dict[str, Any]:
        """
        Executes the autonomous debugging state machine for a job.
        
        State Flow:
        IDLE -> ANALYZING -> INSPECTING -> TESTING -> DIAGNOSING -> FIXING -> VERIFYING -> SUCCESS / FAILED
        """
        start_time = time.time()
        
        # 1. State: INSPECTING
        self.interface.progress(job_id, 10, "inspecting_workspace")
        self.interface.log(job_id, f"Inspecting workspace '{workspace}'", "info")

        tool_descs = self.interface.get_tool_descriptions()
        tool_names = [t["name"] for t in tool_descs]
        self.interface.log(job_id, f"Discovered {len(tool_names)} registered execution tools", "info")

        # Discover source files
        files_list = self.interface.execute_tool("list_files", workspace=workspace)
        if isinstance(files_list, dict) and not files_list.get("success", True):
            error_msg = files_list.get("error", f"Failed to list files in workspace '{workspace}'")
            self.interface.fail(job_id, error_msg)
            return {"success": False, "error": error_msg}

        self.interface.log(job_id, f"Found {len(files_list)} files in workspace: {', '.join(files_list)}", "info")

        # 2. State: TESTING (Initial Baseline Run)
        self.interface.progress(job_id, 25, "running_tests")
        self.interface.log(job_id, "Executing baseline test suite to observe bug", "info")

        test_result = self.tester.execute_suite(workspace)
        if test_result["passed"]:
            msg = "Baseline test suite passed. No bug reproduction observed."
            self.interface.log(job_id, msg, "warning")
            self.interface.complete(job_id, result={
                "verified": True,
                "tests_passed": True,
                "diff": "",
                "message": msg
            })
            return {"success": True, "message": msg}

        self.interface.log(job_id, f"Test suite failed (exit code {test_result['return_code']}). Capturing failure log.", "warning")

        # 3. Read Source File Contents
        source_contents: Dict[str, str] = {}
        for fname in files_list:
            if fname.endswith(".py") and not fname.startswith("test_"):
                try:
                    content = self.interface.execute_tool("read_file", workspace=workspace, file_path=fname)
                    if isinstance(content, str):
                        source_contents[fname] = content
                except Exception:
                    continue

        attempt_history: List[str] = []
        retry_count = 0

        # 4. Retry Loop (Max 3 attempts)
        while retry_count < MAX_RETRIES:
            retry_count += 1
            step_progress = 40 + (retry_count * 15)
            
            # State: DIAGNOSING
            self.interface.progress(job_id, step_progress, f"diagnosing_attempt_{retry_count}")
            self.interface.log(job_id, f"Attempt {retry_count}/{MAX_RETRIES}: Analyzing failure with LLM", "info")

            history_str = "\n".join(attempt_history)
            analysis = self.analyzer.analyze_bug_and_generate_fix(
                bug_report=bug_report,
                files=files_list,
                test_stdout=test_result["stdout"],
                test_stderr=test_result["stderr"],
                source_contents=source_contents,
                attempt_history=history_str
            )

            if not analysis.get("success", False):
                err_msg = analysis.get("error", "LLM diagnosis failed")
                self.interface.log(job_id, f"LLM error: {err_msg}", "error")
                self.interface.fail(job_id, err_msg)
                return {"success": False, "error": err_msg}

            diagnosis = analysis.get("diagnosis", "No diagnosis string provided")
            self.interface.log(job_id, f"Diagnosis: {diagnosis}", "info")

            proposed_changes = analysis.get("proposed_changes", [])
            if not proposed_changes:
                self.interface.log(job_id, "LLM returned no proposed code changes.", "warning")
                attempt_history.append(f"Attempt {retry_count}: LLM proposed no changes.")
                continue

            # State: FIXING
            self.interface.progress(job_id, step_progress + 5, f"applying_fix_attempt_{retry_count}")
            applied_backups: List[Dict[str, Any]] = []

            for change in proposed_changes:
                target_file = change.get("file")
                new_content = change.get("content")
                if not target_file or new_content is None:
                    continue

                self.interface.log(job_id, f"Applying candidate fix to '{target_file}'", "info")
                patch_res = self.coder.apply_patch(workspace, target_file, new_content)
                applied_backups.append(patch_res)

            # State: VERIFYING
            self.interface.progress(job_id, step_progress + 10, f"verifying_attempt_{retry_count}")
            self.interface.log(job_id, f"Running tests to verify fix candidate (Attempt {retry_count})", "info")

            verify_result = self.tester.execute_suite(workspace)

            if verify_result["passed"]:
                # Success! Generate Git diff
                diff_res = self.coder.get_diff(workspace)
                diff_text = diff_res.get("diff", "")

                duration = round(time.time() - start_time, 2)
                self.interface.log(job_id, "Fix verified! All unit tests passed cleanly.", "info")
                self.interface.progress(job_id, 100, "completed")
                
                result_payload = {
                    "verified": True,
                    "tests_passed": True,
                    "retries": retry_count,
                    "diagnosis": diagnosis,
                    "diff": diff_text,
                    "duration": duration
                }
                self.interface.complete(job_id, result=result_payload)
                return {"success": True, "result": result_payload}

            # Verification Failed -> Rollback attempt
            self.interface.log(job_id, f"Attempt {retry_count} failed tests. Rolling back changes.", "warning")
            for patch in applied_backups:
                self.coder.rollback(workspace, patch["file"], patch["backup_content"])

            attempt_history.append(
                f"Attempt {retry_count}: Modified {', '.join([p['file'] for p in applied_backups])} but tests still failed."
            )

        # Max retries exceeded -> FAILED
        fail_msg = f"Fix could not be verified after maximum retry limit ({MAX_RETRIES} attempts)."
        self.interface.log(job_id, fail_msg, "error")
        self.interface.fail(job_id, fail_msg)
        return {"success": False, "error": fail_msg}
