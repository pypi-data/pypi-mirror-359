import enum
import logging
import pathlib
import shlex
import shutil
import subprocess
from datetime import datetime
from typing import Any, Literal

import packaging.version

from ._connection_parameters import MsSqlDatabaseParameters
from ._encoding import BcpEncodingSettings
from ._options import BcpOptions


class _BcpMode(enum.Enum):
    IN = "in"
    OUT = "out"
    QUERY_OUT = "queryout"
    FORMAT = "format"


def _resolve_to_str(value: str | bytes | None | Any) -> str:
    if isinstance(value, bytes):
        value = value.decode()
    value = str(value)
    return value


class BcpProcessError(subprocess.CalledProcessError):
    def __str__(self) -> str:
        error_message = " ; ".join(
            [
                super().__str__(),
                f"stderr={_resolve_to_str(self.stderr)}",
                f"stdout={_resolve_to_str(self.stdout)}",
            ]
        )
        return error_message


class BCP:
    """
    A bcp client, that behind the scenes uses the actual bcp command line tool.
    Usage example:
    >>> import simple_bcp
    >>> bcp = simple_bcp.BCP()
    >>> database_parameters = simple_bcp.MsSqlDatabaseParameters(
    >>>     server_hostname="your-sql-server-hostname",
    >>>     username="user",
    >>>     password="pass"
    >>> )
    >>> output_file_path = bcp.download_table(table_name="your_table_name",
    >>>                                       database_parameters=database_parameters)
    >>> print("downloaded table data is now available at ", output_file_path)
    >>> bcp.upload_into_table(table_name="dest_table_name",
    >>>                       database_parameters=database_parameters,
    >>>                       data_file_path=output_file_path)
    >>> print("the data is now copied to dest_table_name")
    """

    def __init__(self, *, bcp_executable_path: pathlib.Path | str | None = None):
        """
        :param bcp_executable_path:
            Path to the `bcp` executable.
            Defaults to `bcp`, which relies on the system's PATH environment variable.
            Upon init, `bcp -v` command will be run.
        """
        self._init_logger()
        self._init_executable_path(executable_path=bcp_executable_path)
        self._init_bcp_version()

    def _init_logger(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def _init_executable_path(self, *, executable_path: pathlib.Path | str | None):
        if executable_path is None:
            default = shutil.which("bcp")
            if default is None:
                raise FileNotFoundError(
                    "bcp not found in PATH. Add bcp to PATH environment variable or provide executable_path explicitly"
                )
            executable_path = pathlib.Path(default)
        elif isinstance(executable_path, str):
            executable_path = pathlib.Path(executable_path)

        if not executable_path.exists():
            raise FileNotFoundError(f"{executable_path.as_posix()} not found")

        if not executable_path.is_file():
            raise OSError(f"path {executable_path} is not a file")

        self._executable_path = executable_path

    def _init_bcp_version(self):
        result = self._run_bcp_command(["-v"])
        # `bcp -v` output example:
        # BCP Utility for Microsoft SQL Server
        # Copyright (C) Microsoft Corporation. All rights reserved.
        # Version 15.0.2000.5
        raw_version = result.strip().split()[-1]
        self._bcp_version = packaging.version.parse(raw_version)
        self._logger.debug(f"BCP version: {self._bcp_version}", extra={"bcp_version": str(self._bcp_version)})

    def _run_bcp_command(self, command_args: list[str]) -> str:
        command = [self._executable_path.as_posix()] + command_args
        formatted_command = shlex.join(command)
        self._logger.debug(f"Running command: `{formatted_command}`", extra={"bcp_command": formatted_command})
        try:
            result = subprocess.run(command, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise BcpProcessError(returncode=e.returncode, cmd=e.cmd, output=e.output, stderr=e.stderr) from e
        stdout = _resolve_to_str(result.stdout)
        stderr = _resolve_to_str(result.stderr)
        self._logger.debug(
            f"BCP output: stdout={stdout} ; stderr={stderr}",
            extra={"bcp_stdout": stdout, "bcp_stderr": stderr, "bcp_command": formatted_command},
        )
        return stdout

    def _resolve_output_file_path(
        self,
        *,
        path: pathlib.Path | str | None,
        default_filename: str,
    ) -> pathlib.Path:
        if path is None:
            path = pathlib.Path.cwd() / default_filename

        if isinstance(path, str):
            path = pathlib.Path(path)

        directory_path = path.absolute().parent
        if not directory_path.exists():
            raise FileNotFoundError(f"directory {directory_path} does not exist")

        return path

    def _resolve_input_file_path(self, *, path: pathlib.Path | str) -> pathlib.Path:
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path.as_posix()} does not exist")
        if not path.is_file():
            raise OSError(f"{path.as_posix()} is not a file")
        return path

    def _build_command_args(
        self,
        *,
        mode: _BcpMode,
        source: str,
        file_path: pathlib.Path,
        database_parameters: MsSqlDatabaseParameters,
        bcp_encoding_settings: BcpEncodingSettings | None | pathlib.Path | str,
        bcp_options: BcpOptions | None,
    ) -> list[str]:
        if bcp_encoding_settings is None:
            bcp_encoding_settings = BcpEncodingSettings()
        if isinstance(bcp_encoding_settings, BcpEncodingSettings):
            encoding_options = bcp_encoding_settings.command_options
        else:
            bcp_encoding_settings = self._resolve_input_file_path(path=bcp_encoding_settings)
            encoding_options = {"-f": bcp_encoding_settings.as_posix()}

        options = {
            **database_parameters.command_options,
            **(bcp_options or BcpOptions()).command_options,
            **encoding_options,
        }

        if mode is _BcpMode.FORMAT:
            mode_parts = [mode.value, "nul"]
            options["-f"] = file_path.as_posix()
        else:
            mode_parts = [mode.value, file_path.as_posix()]

        command_args = [
            source,
            *mode_parts,
        ]
        for key, value in options.items():
            command_args.append(key)
            if value is not None:
                command_args.append(value)

        return command_args

    def _download(
        self,
        *,
        source: str,
        database_parameters: MsSqlDatabaseParameters,
        output_file_path: pathlib.Path | str | None,
        default_filename_parts: list[str],
        mode: Literal[_BcpMode.OUT, _BcpMode.QUERY_OUT, _BcpMode.FORMAT],
        bcp_encoding_settings: BcpEncodingSettings | None | pathlib.Path | str,
        bcp_options: BcpOptions | None,
    ) -> pathlib.Path:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        default_filename = "-".join(["simple_bcp", *default_filename_parts, timestamp])
        output_file_path = self._resolve_output_file_path(path=output_file_path, default_filename=default_filename)
        command_args = self._build_command_args(
            mode=mode,
            source=source,
            file_path=output_file_path,
            database_parameters=database_parameters,
            bcp_options=bcp_options,
            bcp_encoding_settings=bcp_encoding_settings,
        )
        self._run_bcp_command(command_args)
        return output_file_path

    def download_table(
        self,
        *,
        table_name: str,
        database_parameters: MsSqlDatabaseParameters,
        output_file_path: pathlib.Path | str | None = None,
        bcp_encoding_settings: BcpEncodingSettings | None | pathlib.Path | str = None,
        bcp_options: BcpOptions | None = None,
    ) -> pathlib.Path:
        """
        Download table data using bcp.
        This is equivalent to calling `bcp table_name out ...`.

        :param table_name: The name of the table to download.
            May be of one of 2 formats - either simply `table_name` or `database_name.schema.table_name`.
            Notice: combining `database_name.schema.table_name` table name format and setting
            `database_parameters.database_name` is not allowed by bcp and a `BcpProcessError` may be raised.
        :param database_parameters: database connection details
        :param output_file_path: output the data to this path.
            Defaults to None which means let this package decide on the path.
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`.
            may be a `BcpEncodingSettings` or a path to a format file created with `download_table_format`
        :param bcp_options: options to pass to bcp. See `simple_bcp.BcpOptions`. defaults to `BcpOptions()`.
        :return: the path of the downloaded file
        :raises BcpProcessError: If for any reason the bcp command fails.
        """
        return self._download(
            source=table_name,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            default_filename_parts=[self.download_table.__name__, table_name],
            mode=_BcpMode.OUT,
            bcp_encoding_settings=bcp_encoding_settings,
            bcp_options=bcp_options,
        )

    def download_table_format(
        self,
        *,
        table_name: str,
        database_parameters: MsSqlDatabaseParameters,
        output_file_path: pathlib.Path | str | None = None,
        bcp_encoding_settings: BcpEncodingSettings | None = None,
        bcp_options: BcpOptions | None = None,
    ) -> pathlib.Path:
        """
        Download table format file using bcp.
        This file can be later used for bcp in (`BCP.upload_into_table`) with the argument `bcp_encoding_settings`.
        This is equivalent to calling `bcp table_name format ...`.

        :param table_name: The name of the table to download its format file.
            May be of one of 2 formats - either simply `table_name` or `database_name.schema.table_name`.
            Notice: combining `database_name.schema.table_name` table name format and setting
            `database_parameters.database_name` is not allowed by bcp and a `BcpProcessError` may be raised.
        :param database_parameters: database connection details
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`
        :param bcp_options: options to pass to bcp. See `simple_bcp.BcpOptions`. defaults to `BcpOptions()`.
        :return: the path of the downloaded format file.
        :raises BcpProcessError: If for any reason the bcp command fails.
        """
        return self._download(
            source=table_name,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            default_filename_parts=[self.download_table_format.__name__, table_name],
            mode=_BcpMode.FORMAT,
            bcp_encoding_settings=bcp_encoding_settings,
            bcp_options=bcp_options,
        )

    def download_query(
        self,
        *,
        query: str,
        database_parameters: MsSqlDatabaseParameters,
        output_file_path: pathlib.Path | str | None = None,
        bcp_encoding_settings: BcpEncodingSettings | None | pathlib.Path | str = None,
        bcp_options: BcpOptions | None = None,
    ) -> pathlib.Path:
        """
        Download query result data using bcp.
        This is equivalent to calling `bcp <query> queryout ...`.

        :param query: sql query string.
            It is highly recommended to ensure that your SQL query is properly sanitized,
            in order to avoid security risks such as SQL injection.
            Consider using packages like SQLAlchemy or other parameterized query libraries to build queries safely.
            Table and views names in your query may be of one of 2 formats - either simply `table_name` or
            `database_name.schema.table_name`.
            Notice: combining `database_name.schema.table_name` table name format and setting
            `database_parameters.database_name` is not allowed by bcp and a `BcpProcessError` may be raised.

        :param database_parameters: database connection details
        :param output_file_path: output the data to this path.
                                 Defaults to None which means let this package decide on the path.
        :param bcp_encoding_settings: how to encode the downloaded data. defaults to `EncodingOptions()`
            may be a `BcpEncodingSettings` or a path to a format file created with `download_table_format`
        :param bcp_options: options to pass to bcp. See `simple_bcp.BcpOptions`. defaults to `BcpOptions()`.
        :return: the path of the downloaded file.
        :raises BcpProcessError: If for any reason the bcp command fails.
        """
        return self._download(
            source=query,
            database_parameters=database_parameters,
            output_file_path=output_file_path,
            default_filename_parts=[self.download_query.__name__],
            mode=_BcpMode.QUERY_OUT,
            bcp_encoding_settings=bcp_encoding_settings,
            bcp_options=bcp_options,
        )

    def upload_into_table(
        self,
        *,
        table_name: str,
        database_parameters: MsSqlDatabaseParameters,
        data_file_path: pathlib.Path | str,
        bcp_encoding_settings: BcpEncodingSettings | None | pathlib.Path | str = None,
        bcp_options: BcpOptions | None = None,
    ) -> None:
        """
        Upload data created by bcp (`download_query` or `download_table`) - into a table.
        This is equivalent to calling `bcp table_name in ...`.

        :param table_name: The name of the table to upload to.
            May be of one of 2 formats - either simply `table_name` or `database_name.schema.table_name`.
            Notice: combining `database_name.schema.table_name` table name format and setting
            `database_parameters.database_name` is not allowed by bcp and a `BcpProcessError` may be raised.
        :param database_parameters: database connection details
        :param data_file_path: the path of the data to upload
        :param bcp_encoding_settings: how the uploaded data is encoded. defaults to `EncodingOptions()`
            may be a `BcpEncodingSettings` or a path to a format file created with `download_table_format`
        :param bcp_options: options to pass to bcp. See `simple_bcp.BcpOptions`. defaults to `BcpOptions()`.
        :raises BcpProcessError: If for any reason the bcp command fails.
        """
        data_file_path = self._resolve_input_file_path(path=data_file_path)
        command_args = self._build_command_args(
            mode=_BcpMode.IN,
            source=table_name,
            file_path=data_file_path,
            database_parameters=database_parameters,
            bcp_options=bcp_options,
            bcp_encoding_settings=bcp_encoding_settings,
        )
        self._run_bcp_command(command_args)
