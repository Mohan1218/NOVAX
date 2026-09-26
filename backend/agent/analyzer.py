import os
import json
import re
from typing import Dict, Any, Optional, List
from backend.agent.prompts import SYSTEM_DIAGNOSIS_PROMPT, ANALYSIS_USER_TEMPLATE


def clean_json_text(raw_text: str) -> str:
    """
    Strips markdown code blocks, backticks, and extra whitespace from raw LLM output.
    """
    text = raw_text.strip()
    # Remove markdown code block fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()
    return text


class LLMAnalyzer:
    """
    LLM interaction wrapper supporting Google GenAI (Gemini), OpenAI, or Mock LLM responses.
    """

    def __init__(self, provider: Optional[str] = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.provider = provider or ("gemini" if os.getenv("GEMINI_API_KEY") else ("openai" if os.getenv("OPENAI_API_KEY") else None))

    def analyze_bug_and_generate_fix(
        self,
        bug_report: str,
        files: List[str],
        test_stdout: str,
        test_stderr: str,
        source_contents: Dict[str, str],
        attempt_history: str = ""
    ) -> Dict[str, Any]:
        """
        Queries the configured LLM or mock provider to diagnose a bug and propose candidate code changes.
        """
        # If in Mock mode, return a simulated diagnosis/fix based on inputs
        if self.mock_mode:
            return self._generate_mock_analysis(bug_report, source_contents, test_stdout)

        # Check for missing API key
        if not self.provider or (self.provider == "gemini" and not os.getenv("GEMINI_API_KEY")) or (self.provider == "openai" and not os.getenv("OPENAI_API_KEY")):
            return {
                "success": False,
                "error": "GEMINI_API_KEY environment variable is missing. Please configure GEMINI_API_KEY to execute real LLM debug runs."
            }

        # Format user message
        source_str = "\n\n".join([f"--- FILE: {fname} ---\n{content}" for fname, content in source_contents.items()])
        user_prompt = ANALYSIS_USER_TEMPLATE.format(
            bug_report=bug_report,
            files=", ".join(files),
            test_stdout=test_stdout,
            test_stderr=test_stderr,
            source_contents=source_str,
            attempt_history=attempt_history or "None"
        )

        try:
            if self.provider == "gemini":
                return self._call_gemini(user_prompt)
            elif self.provider == "openai":
                return self._call_openai(user_prompt)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported LLM provider: {self.provider}"
                }
        except Exception as exc:
            return {
                "success": False,
                "error": f"LLM provider error ({self.provider}): {str(exc)}"
            }

    def _call_gemini(self, user_prompt: str) -> Dict[str, Any]:
        """
        Calls Google GenAI SDK (google.genai).
        """
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_DIAGNOSIS_PROMPT}\n\n{user_prompt}"
        )
        
        raw_text = response.text
        cleaned = clean_json_text(raw_text)
        parsed = json.loads(cleaned)
        parsed["success"] = True
        return parsed

    def _call_openai(self, user_prompt: str) -> Dict[str, Any]:
        """
        Calls OpenAI SDK.
        """
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_DIAGNOSIS_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        raw_text = response.choices[0].message.content
        cleaned = clean_json_text(raw_text)
        parsed = json.loads(cleaned)
        parsed["success"] = True
        return parsed

    def _generate_mock_analysis(self, bug_report: str, source_contents: Dict[str, str], test_stdout: str) -> Dict[str, Any]:
        """
        Fallback mock provider for offline automated testing.
        """
        if "calculator.py" in source_contents:
            return {
                "success": True,
                "diagnosis": "Incorrect discount calculation. Subtracted percentage directly instead of computing percentage value.",
                "reasoning": "Discount calculation should compute price * discount_percent / 100 before subtracting.",
                "target_files": ["calculator.py"],
                "proposed_changes": [
                    {
                        "file": "calculator.py",
                        "content": (
                            "def calculate_discount(price, discount_percent):\n"
                            '    """Calculate final price after percentage discount."""\n'
                            "    discount_amount = price * discount_percent / 100\n"
                            "    return price - discount_amount\n"
                        )
                    }
                ]
            }
        return {
            "success": False,
            "error": "Mock LLM: No mock strategy available for given workspace files."
        }
