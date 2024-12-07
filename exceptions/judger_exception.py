class JudgerException(Exception):
    def __init__(
        self,
        question_id: int = None,
        lang: str = None,
        test_case_id: int = None,
        test_case_index: int = None,
        submission_id: int = None,
        status: dict[str, str] = None,
        message: str = '',
        input_file_name: str = '',
        execution_time: float = 0,
        user_output=None,
        expected_output=None
    ) -> None:
        super().__init__()
        self.question_id = question_id
        self.lang = lang
        self.test_case_id = test_case_id
        self.test_case_index = test_case_index
        self.submission_id = submission_id
        self.status = status
        self.input_file_name = input_file_name
        self.message = message
        self.execution_time = execution_time
        self.user_output = user_output
        self.expected_output=expected_output
        
    def get_data(self) -> dict:
        return {
            "question_id": self.question_id,
            "lang": self.lang,
            "test_case_id": self.test_case_id,
            "test_case_index": self.test_case_index,
            "submission_id": self.submission_id,
            "status": self.status,
            "message": self.message,
            "input_file_name": self.input_file_name,
            "execution_time": self.execution_time,
            "user_output": self.user_output,
            "expected_output": self.expected_output,
        }
    
    def __str__(self) -> str:
        status_str = ', '.join(f"{k}: {v}" for k, v in (self.status or {}).items())
        return (
            f"JudgerException:\n"
            f"Question ID: {self.question_id}\n"
            f"Language: {self.lang}\n"
            f"Test Case ID: {self.test_case_id}\n"
            f"Status: {status_str}\n"
            f"Message: {self.message}\n"
            f"Execution Time: {self.execution_time:.2f} seconds\n"
            f"User Output: {self.user_output}\n"
            f"Expected Output: {self.expected_output}"
        )