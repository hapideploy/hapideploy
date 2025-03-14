from hapi.log import BufferStyle


def test_write_and_fetch():
    style = BufferStyle()

    style.write("debug", "Python")
    style.write("debug", "is")
    style.write("debug", "great for DevOps")

    # assert style.fetch() == "Python is great for DevOps."
    fetched = style.fetch()
    assert "Python" in fetched
    assert "is" in fetched
    assert "great for DevOps" in fetched
