import typer

from hapi.core import ArrayInputOutput, InputOutput, Printer, Remote, Task
from hapi.log import Logger


def test_it_creates_an_io_instance():
    io = InputOutput()
    assert io.selector == InputOutput.SELECTOR_ALL
    assert io.stage == InputOutput.STAGE_DEV
    assert io.verbosity == InputOutput.NORMAL

    io = InputOutput("ubuntu-1", "production", InputOutput.DEBUG)
    assert io.selector == "ubuntu-1"
    assert io.stage == "production"
    assert io.verbosity == InputOutput.DEBUG


def test_it_check_verbose_levels():
    io = InputOutput("ubuntu-1", "production", InputOutput.QUIET)
    assert io.quiet() == True
    assert io.normal() == False
    assert io.detail() == False
    assert io.debug() == False

    io = InputOutput("ubuntu-1", "production", InputOutput.NORMAL)
    assert io.quiet() == False
    assert io.normal() == True
    assert io.detail() == False
    assert io.debug() == False

    io = InputOutput("ubuntu-1", "production", InputOutput.DETAIL)
    assert io.quiet() == False
    assert io.normal() == False
    assert io.detail() == True
    assert io.debug() == False

    io = InputOutput("ubuntu-1", "production", InputOutput.DEBUG)
    assert io.quiet() == False
    assert io.normal() == False
    assert io.detail() == False
    assert io.debug() == True


def test_it_decorates_text():
    io = InputOutput()

    text = "IO should support <primary>primary</primary>, <success>success</success>, <info>info</info>, <comment>comment</comment>, <warning>warning</warning> and <danger>danger</danger>."

    expected = f"IO should support {typer.style('primary', fg=typer.colors.CYAN)}, {typer.style('success', fg=typer.colors.GREEN)}, {typer.style('info', fg=typer.colors.BLUE)}, {typer.style('comment', fg=typer.colors.YELLOW)}, {typer.style('warning', fg=typer.colors.YELLOW)} and {typer.style('danger', fg=typer.colors.RED)}."

    decorated = io.decorate(text)

    assert decorated == expected


def test_it_caches_output():
    io = ArrayInputOutput()
    io.writeln("This is the line 1.")
    io.writeln("This is the line 2.")
    io.writeln("This is the line 3.")
    io.write("One more line")

    assert io.items == [
        "This is the line 1.\n",
        "This is the line 2.\n",
        "This is the line 3.\n",
        "One more line",
    ]


def test_it_prints_task():
    records = []

    class TestingStyle(Logger):
        def write(self, level: str, message: str, context: dict = None):
            records.append(
                dict(
                    level=level,
                    message=message,
                    context=context,
                )
            )

    remote = Remote(host="192.168.33.11", user="vagrant")
    task = Task("sample", "This is a sample task", lambda _: None)
    io = ArrayInputOutput(verbosity=InputOutput.NORMAL)
    log = TestingStyle()

    printer = Printer(io, log)

    printer.print_task(remote, task)

    record = records[0]

    assert record["level"] == Logger.LEVEL_DEBUG
    assert record["message"] == "[192.168.33.11] TASK sample"
    assert record["context"] is None

    item = io.items[0]

    assert item == InputOutput.decorate(
        f"[<primary>192.168.33.11</primary>] <success>TASK</success> sample" + "\n"
    )


def test_it_prints_command():
    records = []

    class TestingStyle(Logger):
        def write(self, level: str, message: str, context: dict = None):
            records.append(
                dict(
                    level=level,
                    message=message,
                    context=context,
                )
            )

    remote = Remote(host="192.168.33.11", user="vagrant")
    command = "if [ ! -d ~/deploy/dev/.dep ]; then echo +true; fi"
    io = ArrayInputOutput(verbosity=InputOutput.DETAIL)
    log = TestingStyle()

    printer = Printer(io, log)

    printer.print_command(remote, command)

    record = records[0]

    assert record["level"] == Logger.LEVEL_DEBUG
    assert (
        record["message"]
        == "[192.168.33.11] RUN if [ ! -d ~/deploy/dev/.dep ]; then echo +true; fi"
    )
    assert record["context"] is None

    item = io.items[0]

    assert item == InputOutput.decorate(
        f"[<primary>192.168.33.11</primary>] <comment>RUN</comment> if [ ! -d ~/deploy/dev/.dep ]; then echo +true; fi"
        + "\n"
    )


def test_it_prints_line():
    records = []

    class TestingStyle(Logger):
        def write(self, level: str, message: str, context: dict = None):
            records.append(
                dict(
                    level=level,
                    message=message,
                    context=context,
                )
            )

    remote = Remote(host="192.168.33.11", user="vagrant")
    line = "+true"
    io = ArrayInputOutput(verbosity=InputOutput.DEBUG)
    log = TestingStyle()

    printer = Printer(io, log)

    printer.print_line(remote, line)

    record = records[0]

    assert record["level"] == Logger.LEVEL_DEBUG
    assert record["message"] == "[192.168.33.11] +true"
    assert record["context"] is None

    item = io.items[0]

    assert item == InputOutput.decorate(
        f"[<primary>192.168.33.11</primary>] +true" + "\n"
    )


def test_it_prints_info():
    records = []

    class TestingStyle(Logger):
        def write(self, level: str, message: str, context: dict = None):
            records.append(
                dict(
                    level=level,
                    message=message,
                    context=context,
                )
            )

    remote = Remote(host="192.168.33.11", user="vagrant")
    msg = "Deployment is started"
    io = ArrayInputOutput(verbosity=InputOutput.NORMAL)
    log = TestingStyle()

    printer = Printer(io, log)

    printer.print_info(remote, msg)

    record = records[0]

    assert record["level"] == Logger.LEVEL_DEBUG
    assert record["message"] == "[192.168.33.11] INFO Deployment is started"
    assert record["context"] is None

    item = io.items[0]

    assert item == InputOutput.decorate(
        f"[<primary>192.168.33.11</primary>] <info>INFO</info> Deployment is started"
        + "\n"
    )
