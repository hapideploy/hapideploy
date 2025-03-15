import typer

from hapi import InputOutput
from hapi.core.io import CacheInputOutput


def test_it_creates_an_io_instance():
    io = InputOutput()
    assert io.selector == InputOutput.SELECTOR_DEFAULT
    assert io.stage == InputOutput.STAGE_DEFAULT
    assert io.verbosity == InputOutput.NORMAL

    io = InputOutput("ubuntu-1", "production", InputOutput.DEBUG)
    assert io.selector == "ubuntu-1"
    assert io.stage == "production"
    assert io.verbosity == InputOutput.DEBUG


def test_it_decorates_text():
    io = InputOutput()

    text = "IO should support <primary>primary</primary>, <success>success</success>, <info>info</info>, <comment>comment</comment>, <warning>warning</warning> and <danger>danger</danger>."

    expected = f"IO should support {typer.style('primary', fg=typer.colors.CYAN)}, {typer.style('success', fg=typer.colors.GREEN)}, {typer.style('info', fg=typer.colors.BLUE)}, {typer.style('comment', fg=typer.colors.YELLOW)}, {typer.style('warning', fg=typer.colors.YELLOW)} and {typer.style('danger', fg=typer.colors.RED)}."

    decorated = io.decorate(text)

    assert decorated == expected


def test_it_caches_output():
    io = CacheInputOutput()
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
