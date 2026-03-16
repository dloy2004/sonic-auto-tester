import paramiko


class SSHClient:
    """Thin paramiko wrapper that connects to a SONiC switch and runs commands."""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self._client = None

    def connect(self) -> None:
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )

    def run_command(self, command: str) -> str:
        _, stdout, _ = self._client.exec_command(command)
        return stdout.read().decode()

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
