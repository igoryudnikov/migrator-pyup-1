import asyncio
from .utils import get_logger

logger = get_logger()


async def async_run(shell_command):
    process = await asyncio.create_subprocess_shell(
        shell_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    logger.debug('command: %s, exitcode: %s, stdout: %s, stderr: %s',
                 shell_command, process.returncode, stdout, stderr)

    return stdout, stderr, process.returncode
