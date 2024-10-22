class JudgerException(Exception):
    def __init__(
        self,
        status: dict[str, str],
        message: str = '',
        execution_time = 0,
    ) -> None:
        super().__init__()
        self.status = status
        self.message = message
        self.execution_time = execution_time
