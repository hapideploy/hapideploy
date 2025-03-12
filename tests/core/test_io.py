from hapi import InputOutput


def test_constructor():
    io = InputOutput("all", "dev", InputOutput.NORMAL)

    assert io.selector == "all"
    assert io.stage == "dev"
    assert io.verbosity == InputOutput.NORMAL
