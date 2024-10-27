class JudgerException(Exception):
    def __init__(
        self,
        issue_id: int = None,
        lang: str = None,
        testcase_id: int = None,
        submission_id: int = None,
        status: dict[str, str] = None,
        message: str = '',
        execution_time: float = 0,
        user_output=None,
        expected_output=None
    ) -> None:
        super().__init__()
        self.issue_id = issue_id
        self.lang = lang
        self.testcase_id = testcase_id
        self.submission_id = submission_id
        self.status = status
        self.message = message
        self.execution_time = execution_time
        self.user_output = user_output
        self.expected_output=expected_output
        
    def get_data(self) -> dict:
        return {
            "issue_id": self.issue_id,
            "lang": self.lang,
            "testcase_id": self.testcase_id,
            "submission_id": self.submission_id,
            "status": self.status,
            "message": self.message,
            "execution_time": self.execution_time,
            "user_output": self.user_output,
            "expected_output": self.expected_output,
        }
    
    def __str__(self) -> str:
        status_str = ', '.join(f"{k}: {v}" for k, v in (self.status or {}).items())
        return (
            f"JudgerException:\n"
            f"Issue ID: {self.issue_id}\n"
            f"Language: {self.lang}\n"
            f"Test Case ID: {self.testcase_id}\n"
            f"Status: {status_str}\n"
            f"Message: {self.message}\n"
            f"Execution Time: {self.execution_time:.2f} seconds\n"
            f"User Output: {self.user_output}\n"
            f"Expected Output: {self.expected_output}"
        )