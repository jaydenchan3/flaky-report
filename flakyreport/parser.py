import xml.etree.ElementTree as ET


def parse_file(path):
    """Return a list of ((classname, name), outcome) for every testcase in a JUnit XML file.

    outcome follows JUnit: "fail" for a <failure> or <error> child, "skip" for <skipped>,
    otherwise "pass" (so <system-out> and similar children don't count as failures).
    Raises ET.ParseError for malformed or empty files; the caller decides what to do.
    """
    root = ET.parse(path).getroot()
    results = []
    # iter() finds testcases at any depth, so <testsuites> and bare <testsuite> roots both work.
    for case in root.iter("testcase"):
        test_id = (case.get("classname"), case.get("name"))
        if case.find("failure") is not None or case.find("error") is not None:
            outcome = "fail"
        elif case.find("skipped") is not None:
            outcome = "skip"
        else:
            outcome = "pass"
        results.append((test_id, outcome))
    return results
