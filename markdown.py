def RegExp(pattern, flags):
    """
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp
    """
    return host_eval("(p, f) => new RegExp(p, f)")(pattern, flags)

re = RegExp(
    "^(?:---\\s*([\\s\\S]*?)\\s*---)?\\s*(?:# (.+))?\\s*(?:## (.+))?\\s*([\\s\\S]*)?$",
    "m"
)

def split_markdown(md):
    """
    Split the markdown into subsections for further processing.

    Pounds _must_ be followed by a space.
    """
    global re
    matches = re.exec(md.rstrip())

    if not matches:
        raise Exception("No match found.", md)

    def get(i):
        return matches[i].strip() if matches[i] else ""

    front_matter = get(1)
    title        = get(2)
    subtitle     = get(3)
    content      = get(4)

    return front_matter, title, subtitle, content

def parse_front_matter(fm):
    # Construct a JS object from the front matter
    # Here the parens are essential, without them curly braces
    # indicate block scope thus : raises a SyntaxError.
    # WARNING: Dragons, obviously.
    obj = '({' + ','.join(fm.split('\n')) + '})'
    # TODO: Add a 'dict' JS function to force cast to dict (just add
    # the runtime dict property)
    return host_eval(obj)

def tester(test):
    """Split the markdown and restore markup."""
    try:
        front_matter, title, subtitle, content = split_markdown('\n'.join(test))
    except Exception:
        return (-1, -1, -1, -1)

    if front_matter:
        # NOTE: Empty front matter not allowed
        front_matter = "---\n" + front_matter + "\n---"
    if title:
        title = "# " + title
    if subtitle:
        subtitle = "## " + subtitle

    return front_matter, title, subtitle, content

# Each test is a 4-tuple (front_matter, title, subtitle, content)
test1 = ("", "# Title", "## Subtitle", "")
test2 = ("", "# Title", "## Subtitle", "Content")
test3 = ("---\nfoo: bar\n---", "# Title", "## Title", "Content")
test3 = ("---\nfoo: bar\nbar: baz\n---", "# Title", "## Subtitle",
         "Content\n- A\n- B")
test6 = ("", "", "", "")
test7 = ("", "# Title", "", "Content")

test4 = ("", "#Title", "##Subtitle", "")
test5 = ("---\nfoo: bar\n", "# Title", "## Subtitle", "Content")


def run_tests():
    # Split
    assert test1 == tester(test1)
    assert test2 == tester(test2)
    assert test3 == tester(test3)
    assert test6 == tester(test6)
    assert test7 == tester(test7)

    assert test4 != tester(test4)
    assert test5 != tester(test5)

    # Front matter
    assert parse_front_matter("foo: 1").foo == 1
    assert parse_front_matter("foo: 1\nbar: 'hehe'").bar == "hehe"
