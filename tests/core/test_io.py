from hapi import InputOutput


def test_it_creates_an_input_output_instance():
    io = InputOutput("all", "dev", InputOutput.NORMAL)

    assert io.selector == "all"
    assert io.stage == "dev"
    assert io.verbosity == InputOutput.NORMAL
