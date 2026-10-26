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


def load_runs(directory):
    """Parse every *.xml file in directory.

    Returns (runs, skipped): runs is one parse_file() result per readable file, and
    skipped is [(path, reason)] for files that could not be read or parsed.
    Only ParseError and OSError are caught, so bugs in this code still fail loudly.
    """
    runs, skipped = [], []
    for path in sorted(directory.glob("*.xml")):
        try:
            runs.append(parse_file(path))
        except ET.ParseError as e:
            skipped.append((path, f"not valid XML ({e})"))
        except OSError as e:
            skipped.append((path, f"could not read ({e})"))
    return runs, skipped
