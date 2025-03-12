from hapi.log import BufferStyle


def test_write_and_fetch():
    style = BufferStyle()

    style.write("Python")
    style.write(" ")
    style.write("is")
    style.write(" ")
    style.write("great for DevOps")
    style.write(".")

    assert style.fetch() == "Python is great for DevOps."
    assert style.buffered == ""


def test_writeln_and_fetch():
    style = BufferStyle()

    style.writeln("Hello")
    style.writeln("How are you?")
    style.writeln("I'm fine. Thanks!")

    assert style.fetch() == "Hello\nHow are you?\nI'm fine. Thanks!\n"
    assert style.buffered == ""
