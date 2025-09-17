# ngs_core/wrapper.py

import argparse
import shlex
import subprocess
import sys

import structlog

from ngs_core.logging_setup import setup_logging

setup_logging()
log = structlog.get_logger()


def main():
    parser = argparse.ArgumentParser(
        description="A generic wrapper for running and logging commands.",
        add_help=False,
    )
    parser.add_argument("--task-id", help="Nextflow task ID for context.", default="local")
    parser.add_argument("--process-name", help="Nextflow process name.", default="unknown")

    args, command_to_run = parser.parse_known_args()

    if command_to_run and command_to_run[0] == "--":
        command_to_run.pop(0)

    if not command_to_run:
        log.error("wrapper.error", reason="No command provided to execute.")
        sys.exit(1)

    structlog.contextvars.bind_contextvars(
        task_id=args.task_id, process_name=args.process_name, tool_name=command_to_run[0]
    )

    # --- REFINEMENT 1: Use shlex.join() for accurate command logging ---
    log.info("task.started", command=shlex.join(command_to_run))

    exit_code = -1
    try:
        process = subprocess.Popen(
            command_to_run,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if process.stdout is None:
            raise RuntimeError("Failed to capture stdout of the subprocess.")

        for line in process.stdout:
            # Skip logging empty lines
            stripped_line = line.strip()
            if stripped_line:
                log.info("tool.output", raw_message=stripped_line)

        process.wait()
        exit_code = process.returncode

        if exit_code != 0:
            raise subprocess.CalledProcessError(exit_code, command_to_run)

    except Exception:
        log.exception("task.failed", exit_code=exit_code)
        sys.exit(exit_code or 1)
    finally:
        if exit_code == 0:
            log.info("task.succeeded", exit_code=exit_code)


if __name__ == "__main__":
    main()
