from hapi.utils import env_stringify, extract_curly_brackets


def test_env_stringify():
    env = dict(
        LIB_NAME="HapiDeploy",
        LIB_VERSION="1.0.0.dev",
        LIB_DESC="A remote execution tool",
        LIB_YEAR=2025,
    )

    assert (
        env_stringify(env)
        == "LIB_NAME=HapiDeploy LIB_VERSION=1.0.0.dev LIB_DESC='A remote execution tool' LIB_YEAR=2025"
    )


def test_extract_curly_brackets():
    keys = extract_curly_brackets("cd {{release_path}} && {{bin/npm}} run install")

    assert keys == ["release_path", "bin/npm"]
