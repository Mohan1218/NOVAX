from typing import Dict, Any
from backend.services.agent_interface import AgentBackendInterface


class TesterAgent:
    """
    Agent sub-component responsible for executing test suites and parsing failure evidence.
    Must operate ONLY through AgentBackendInterface.
    """

    def __init__(self, interface: AgentBackendInterface):
        self.interface = interface

    def execute_suite(self, workspace: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Executes pytest suite using AgentBackendInterface tool runner.
        
        Args:
            workspace: Target workspace identifier.
            timeout: Test run timeout in seconds.
            
        Returns:
            Structured test execution summary containing pass/fail boolean, return_code, stdout, stderr.
        """
        test_result = self.interface.execute_tool("run_tests", workspace=workspace, timeout=timeout)
        
        # Parse output for summary
        passed = test_result.get("success", False)
        stdout = test_result.get("stdout", "")
        stderr = test_result.get("stderr", "")
        
        return {
            "passed": passed,
            "return_code": test_result.get("return_code", -1),
            "stdout": stdout,
            "stderr": stderr,
            "duration": test_result.get("duration", 0.0),
            "timed_out": test_result.get("timed_out", False)
        }
