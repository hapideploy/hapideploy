from hapi.core import RunOptions, env_stringify


def test_env_stringify_function():
    env = dict(
        LIB_NAME="HapiDeploy",
        LIB_VERSION="1.0.0.dev",
        LIB_DESC="It is a modern deployment tool.",
        LIB_YEAR=2025
    )

    assert (
        env_stringify(env)
        == "LIB_NAME=HapiDeploy LIB_VERSION=1.0.0.dev LIB_DESC='It is a modern deployment tool.' LIB_YEAR=2025"
    )


def test_run_options_env_property():
    options = RunOptions()
    assert options.env is None

    options = RunOptions(dict(LIB_NAME="HapiDeploy", LIB_VERSION="1.0.0.dev"))

    assert options.env == dict(LIB_NAME="HapiDeploy", LIB_VERSION="1.0.0.dev")
