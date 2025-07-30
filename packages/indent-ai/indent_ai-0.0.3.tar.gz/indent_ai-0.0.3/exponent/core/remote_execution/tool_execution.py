import uuid
from pathlib import Path
from time import time

from anyio import Path as AsyncPath

from exponent.core.remote_execution import files
from exponent.core.remote_execution.cli_rpc_types import (
    BashToolInput,
    BashToolResult,
    ErrorToolResult,
    GlobToolInput,
    GlobToolResult,
    GrepToolInput,
    GrepToolResult,
    ListToolInput,
    ListToolResult,
    ReadToolInput,
    ReadToolResult,
    ToolInputType,
    ToolResultType,
    WriteToolInput,
    WriteToolResult,
)
from exponent.core.remote_execution.code_execution import execute_code
from exponent.core.remote_execution.file_write import execute_full_file_rewrite
from exponent.core.remote_execution.types import CodeExecutionRequest
from exponent.core.remote_execution.utils import (
    assert_unreachable,
    safe_read_file,
    truncate_output,
)

GREP_MAX_RESULTS = 100


async def execute_tool(
    tool_input: ToolInputType, working_directory: str
) -> ToolResultType:
    if isinstance(tool_input, ReadToolInput):
        return await execute_read_file(tool_input, working_directory)
    elif isinstance(tool_input, WriteToolInput):
        return await execute_write_file(tool_input, working_directory)
    elif isinstance(tool_input, ListToolInput):
        return await execute_list_files(tool_input, working_directory)
    elif isinstance(tool_input, GlobToolInput):
        return await execute_glob_files(tool_input, working_directory)
    elif isinstance(tool_input, GrepToolInput):
        return await execute_grep_files(tool_input, working_directory)
    elif isinstance(tool_input, BashToolInput):
        return await execute_bash_tool(tool_input, working_directory)
    else:
        assert_unreachable(tool_input)


def truncate_result[T: ToolResultType](tool_result: T) -> T:
    if isinstance(tool_result, ReadToolResult):
        tool_result.content = truncate_output(tool_result.content)[0]
    if isinstance(tool_result, WriteToolResult):
        tool_result.message = truncate_output(tool_result.message)[0]
    if isinstance(tool_result, BashToolResult):
        tool_result.shell_output = truncate_output(tool_result.shell_output)[0]
    return tool_result


async def execute_read_file(
    tool_input: ReadToolInput, working_directory: str
) -> ReadToolResult | ErrorToolResult:
    file = AsyncPath(working_directory, tool_input.file_path)
    exists = await file.exists()

    if not exists:
        return ErrorToolResult(
            error_message="File not found",
        )

    if await file.is_dir():
        return ErrorToolResult(
            error_message=f"{await file.absolute()} is a directory",
        )

    content = await safe_read_file(file)
    offset = tool_input.offset or 0
    limit = tool_input.limit or -1

    content_lines = content.splitlines()

    content_lines = content_lines[offset:]
    content_lines = content_lines[:limit]

    final_content = "\n".join(content_lines)

    return ReadToolResult(
        content=final_content,
        num_lines=len(final_content.splitlines()),
        start_line=offset,
        total_lines=len(content.splitlines()),
    )


async def execute_write_file(
    tool_input: WriteToolInput, working_directory: str
) -> WriteToolResult:
    file_path = tool_input.file_path
    path = Path(working_directory, file_path)
    result = await execute_full_file_rewrite(
        path, tool_input.content, working_directory
    )
    return WriteToolResult(message=result)


async def execute_list_files(
    tool_input: ListToolInput, working_directory: str
) -> ListToolResult:
    filenames = [entry.name async for entry in AsyncPath(tool_input.path).iterdir()]

    return ListToolResult(
        files=[filename for filename in filenames],
    )


async def execute_glob_files(
    tool_input: GlobToolInput, working_directory: str
) -> GlobToolResult:
    # async timer
    start_time = time()
    results = await files.glob(
        path=working_directory if tool_input.path is None else tool_input.path,
        glob_pattern=tool_input.pattern,
    )
    duration_ms = int((time() - start_time) * 1000)
    return GlobToolResult(
        filenames=results,
        duration_ms=duration_ms,
        num_files=len(results),
        truncated=len(results) >= files.GLOB_MAX_COUNT,
    )


async def execute_grep_files(
    tool_input: GrepToolInput, working_directory: str
) -> GrepToolResult:
    results = await files.search_files(
        path_str=working_directory if tool_input.path is None else tool_input.path,
        file_pattern=tool_input.include,
        regex=tool_input.pattern,
        working_directory=working_directory,
    )
    return GrepToolResult(
        matches=results[:GREP_MAX_RESULTS],
        truncated=bool(len(results) > GREP_MAX_RESULTS),
    )


async def execute_bash_tool(
    tool_input: BashToolInput, working_directory: str
) -> BashToolResult:
    start_time = time()
    result = await execute_code(
        CodeExecutionRequest(
            language="shell",
            content=tool_input.command,
            timeout=tool_input.timeout or 60,
            correlation_id=str(uuid.uuid4()),
        ),
        working_directory=working_directory,
        session=None,  # type: ignore
        should_halt=None,
    )
    return BashToolResult(
        shell_output=result.content,
        exit_code=result.exit_code,
        duration_ms=int((time() - start_time) * 1000),
        timed_out=result.cancelled_for_timeout,
        stopped_by_user=result.halted,
    )
