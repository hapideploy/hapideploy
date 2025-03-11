from hapi import InputOutput


def test_constructor():
    io = InputOutput("all", "main", "dev", InputOutput.VERBOSITY_DEBUG)

    assert io.selector == "all"
    assert io.branch == "main"
    assert io.stage == "dev"
    assert io.verbosity == InputOutput.VERBOSITY_DEBUG
