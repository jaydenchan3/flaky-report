import xml.etree.ElementTree as ET


def parse_file(path):
    """Return a list of ((classname, name), outcome) for every testcase in a JUnit XML file.

    outcome is "pass" if the testcase has no child elements, otherwise "fail".
    Raises ET.ParseError for malformed or empty files; the caller decides what to do.
    """
    root = ET.parse(path).getroot()
    results = []
    # iter() finds testcases at any depth, so <testsuites> and bare <testsuite> roots both work.
    for case in root.iter("testcase"):
        test_id = (case.get("classname"), case.get("name"))
        outcome = "fail" if len(case) > 0 else "pass"
        results.append((test_id, outcome))
    return results
