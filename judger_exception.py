class JudgerException(Exception):
    def __init__(
        self,
        status: dict[str, str],
        message: str = '',
        execution_time: float = 0,
        output=None,
    ) -> None:
        super().__init__()
        self.status = status
        self.message = message
        self.execution_time = execution_time
        self.output = output

    def __str__(self) -> str:
        return (
            f"JudgerException:\n"
            f"  Status: {self.status}\n"
            f"  Message: {self.message}\n"
            f"  Execution Time: {self.execution_time}s\n"
            f"  Output: {self.output}"
        )
