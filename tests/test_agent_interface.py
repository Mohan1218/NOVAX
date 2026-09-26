import pytest
import shutil
from pathlib import Path
from backend.services.agent_interface import AgentBackendInterface
from backend.tools import get_workspace_root, write_file


@pytest.fixture
def interface():
    return AgentBackendInterface()


@pytest.fixture(autouse=True)
def clean_demo_project():
    buggy_code = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    return price - discount_percent\n'
    )
    write_file("demo_project", "calculator.py", buggy_code)
    yield
    write_file("demo_project", "calculator.py", buggy_code)


def test_agent_interface_job_lifecycle(interface):
    # 1. create_job
    job = interface.create_job("demo_project")
    assert isinstance(job, dict)
    job_id = job["job_id"]
    assert job["workspace"] == "demo_project"
    assert job["status"] == "queued"

    # 2. get_job
    fetched = interface.get_job(job_id)
    assert fetched["job_id"] == job_id

    # 3. log
    assert interface.log(job_id, "Executing test agent log", level="info") is True
    logs = [l["message"] for l in interface.get_job(job_id)["logs"] if isinstance(l, dict)]
    assert "Executing test agent log" in logs

    # 4. progress
    assert interface.progress(job_id, 50, "running_tests") is True
    updated = interface.get_job(job_id)
    assert updated["progress"] == 50
    assert updated["current_step"] == "running_tests"

    # 5. complete
    assert interface.complete(job_id, result={"success": True}) is True
    completed = interface.get_job(job_id)
    assert completed["status"] == "completed"
    assert completed["progress"] == 100

    # 6. fail
    job2 = interface.create_job("demo_project")
    assert interface.fail(job2["job_id"], "Test execution error") is True
    failed = interface.get_job(job2["job_id"])
    assert failed["status"] == "failed"
    assert failed["error"] == "Test execution error"


def test_agent_interface_tools(interface):
    # list_files
    files = interface.execute_tool("list_files", workspace="demo_project")
    assert "calculator.py" in files

    # read_file
    content = interface.execute_tool("read_file", workspace="demo_project", file_path="calculator.py")
    assert "calculate_discount" in content

    # run_tests
    test_res = interface.execute_tool("run_tests", workspace="demo_project")
    assert test_res["success"] is False

    # get_tool_descriptions
    descs = interface.get_tool_descriptions()
    assert isinstance(descs, list)
    tool_names = [d["name"] for d in descs]
    assert "list_files" in tool_names
    assert "run_tests" in tool_names

    # unknown tool
    unknown_res = interface.execute_tool("invalid_unknown_tool_xyz", workspace="demo_project")
    assert unknown_res["success"] is False
    assert "Unknown tool" in unknown_res["error"]

    # invalid job id
    assert interface.get_job("invalid_job_id_999") is None
    assert interface.log("invalid_job_id_999", "msg") is False


def test_agent_interface_full_integration_workflow(interface):
    """
    Complete backend-only integration test verifying Member 1 can execute the full workflow
    using ONLY AgentBackendInterface.
    """
    # 1. create job
    job = interface.create_job("demo_project")
    job_id = job["job_id"]
    assert job["status"] == "queued"

    # 2. add log
    interface.log(job_id, "Starting automated debugging cycle", "info")

    # 3. set progress
    interface.progress(job_id, 10, "inspecting_workspace")

    # 4. list files
    files = interface.execute_tool("list_files", workspace="demo_project")
    assert "calculator.py" in files

    # 5. read calculator.py
    code = interface.execute_tool("read_file", workspace="demo_project", file_path="calculator.py")
    assert "return price - discount_percent" in code

    # 6. run tests
    interface.progress(job_id, 30, "running_tests")
    test_buggy = interface.execute_tool("run_tests", workspace="demo_project")

    # 7. verify buggy test fails
    assert test_buggy["success"] is False
    assert test_buggy["return_code"] == 1

    # 8. apply known correct fix
    interface.progress(job_id, 60, "applying_fix")
    fixed_code = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    discount_amount = price * discount_percent / 100\n'
        '    return price - discount_amount\n'
    )
    patch_res = interface.execute_tool("apply_file_change", workspace="demo_project", file_path="calculator.py", new_content=fixed_code)
    assert patch_res["success"] is True
    backup_content = patch_res["backup_content"]

    # 9. run tests
    test_fixed = interface.execute_tool("run_tests", workspace="demo_project")

    # 10. verify success
    assert test_fixed["success"] is True
    assert test_fixed["return_code"] == 0

    # 11. get git diff
    diff_res = interface.execute_tool("git_diff", workspace="demo_project")
    assert diff_res["success"] is True
    assert "+    discount_amount = price * discount_percent / 100" in diff_res["diff"]

    # 12. rollback
    interface.progress(job_id, 90, "rolling_back")
    rollback_res = interface.execute_tool("rollback_change", workspace="demo_project", file_path="calculator.py", backup_content=backup_content)
    assert rollback_res["success"] is True

    # 13. run tests
    test_restored = interface.execute_tool("run_tests", workspace="demo_project")

    # 14. verify buggy state restored
    assert test_restored["success"] is False

    # 15. mark job completed
    assert interface.complete(job_id, result={"verified_patch_workflow": True}) is True
    final_job = interface.get_job(job_id)
    assert final_job["status"] == "completed"
    assert final_job["progress"] == 100
    assert final_job["result"] == {"verified_patch_workflow": True}
