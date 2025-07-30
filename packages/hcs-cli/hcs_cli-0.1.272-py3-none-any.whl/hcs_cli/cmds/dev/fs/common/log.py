import functools

import click
from hcs_core.ctxp.util import CtxpException, print_error


def good(msg):
    click.secho("✅", fg="green", nl=False)
    click.echo(" " + msg)


def warn(msg):
    click.secho("⚠️", fg="yellow", nl=False)
    click.echo(" " + msg)


def info(msg):
    click.secho("ℹ️ " + msg)


# icons = ["💡", "✅", "⚠️", "ℹ️", "❌", "🚀", "🔔", "🔍", "📝", "📦"]


def trivial(msg):
    click.secho(click.style(msg, fg="bright_black"))


_failure_printed = False
_step_name = ""


def fail(msg, e: Exception = None):
    if e:
        print_error(e)
    click.secho("❌", fg="red", nl=False)
    click.echo(" " + msg)
    global _failure_printed
    _failure_printed = True
    raise CtxpException()


def step(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        click.secho(f"📦 {func.__name__}")
        global _step_name, _failure_printed
        if _step_name:
            raise CtxpException(
                f"Nested steps are not allowed. Existing step={_step_name}, entering step={func.__name__}"
            )
        _failure_printed = False
        _step_name = func.__name__
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not _failure_printed:
                print()
                fail(f"Step '{func.__name__}' failed", e)
            raise
        finally:
            _step_name = None

    return wrapper
