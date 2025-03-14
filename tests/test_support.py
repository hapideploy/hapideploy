from hapi.support import extract_curly_braces


def test_extract_curly_braces():
    keys = extract_curly_braces("cd {{release_path}} && {{bin/npm}} run install")

    assert keys == ["release_path", "bin/npm"]
