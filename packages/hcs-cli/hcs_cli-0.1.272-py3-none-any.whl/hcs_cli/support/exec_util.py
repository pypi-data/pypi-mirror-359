import os
import subprocess

import click


def exec(cmd, logOnError=True, raise_on_error=True, inherit_output=False):
    click.echo(click.style(f"COMMAND: {cmd}", fg="bright_black"))
    if inherit_output:
        result = subprocess.run(
            cmd.split(" "),
            env=os.environ.copy(),
        )
    else:
        result = subprocess.run(
            cmd.split(" "),
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )

    if result.returncode != 0:
        if logOnError:
            click.echo(f"  RETURN: {result.returncode}")
            if not inherit_output:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    click.echo(f"  STDOUT:      {stdout}")
                if stderr:
                    click.echo(f"  STDERR:      {stderr}")
        if raise_on_error:
            raise click.ClickException(f"Command '{cmd}' failed with return code {result.returncode}.")
    return result
