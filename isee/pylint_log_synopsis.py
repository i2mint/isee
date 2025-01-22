"""
This module provides utilities for working with pylint logs.

Functions:
- parsed_lines: Parse the pylint log lines.
- missing_import_module: Get the missing import module from the log message.
- process_parsed_line: Process the parsed line to get the missing package or module.
- analyze_log: Analyze the pylint log to get the missing packages and modules.
- log_analysis_string: Generate a string report of the missing packages and modules.
- print_log_analysis: Print the string report of the missing packages and modules.
- print_report_followed_by_log: Print the string report followed by the pylint log.


Notes (TODO):

I'd rather have a "here's what you got to do" synopsis.

For example, consider the log below versus the following synopsis of it.

Synopsis:

```
Missing module docstrings in:
- __init__.py
- snippers.py

Missing packages:
- sklearn
- matplotlib
- pandas
```

Log:

```
Run pylint ./$PROJECT_NAME --ignore=tests,examples,scrap --disable=all --enable=C0114,E0401
************* Module slang
slang/__init__.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module slang.snippers
slang/snippers.py:1:0: C0114: Missing module docstring (missing-module-docstring)
slang/snippers.py:6:0: E0401: Unable to import 'sklearn.decomposition' (import-error)
slang/snippers.py:7:0: E0401: Unable to import 'sklearn.discriminant_analysis' (import-error)
slang/snippers.py:8:0: E0401: Unable to import 'sklearn.cluster' (import-error)
************* Module slang.spectrop
slang/spectrop.py:1:0: C0114: Missing module docstring (missing-module-docstring)
slang/spectrop.py:7:0: E0401: Unable to import 'sklearn.decomposition' (import-error)
slang/spectrop.py:8:0: E0401: Unable to import 'sklearn.discriminant_analysis' (import-error)
slang/spectrop.py:9:0: E0401: Unable to import 'sklearn.utils.validation' (import-error)
slang/spectrop.py:10:0: E0401: Unable to import 'sklearn.base' (import-error)
slang/spectrop.py:503:0: E0401: Unable to import 'sklearn.neighbors' (import-error)
slang/spectrop.py:504:0: E0401: Unable to import 'sklearn.discriminant_analysis' (import-error)
slang/spectrop.py:505:0: E0401: Unable to import 'sklearn.decomposition' (import-error)
slang/spectrop.py:506:0: E0401: Unable to import 'sklearn.linear_model' (import-error)
************* Module slang.snip_stats
slang/snip_stats.py:1:0: C0114: Missing module docstring (missing-module-docstring)
slang/snip_stats.py:6:0: E0401: Unable to import 'matplotlib.pylab' (import-error)
slang/snip_stats.py:8:0: E0401: Unable to import 'pandas' (import-error)
slang/snip_stats.py:9:0: E0401: Unable to import 'sklearn.base' (import-error)

-----------------------------------
Your code has been rated at 9.42/10

Error: Process completed with exit code 18.
```

I'd still want the verbose output. But a synopsis report would more immediately useful.

https://github.com/i2mint/unbox has a function that compares deps of setup.cfg versus
imports to give a list of missing third party packages.
That could be used (though different from E0401).

But perhaps a log parser would be better, more generally useable.

Perhaps pylint already has such a synopsis report maker?
"""

import re

colon_pattern = ":".join(f"(?P<{k}>[^:]*)" for k in "path line char code msg".split())
line_parse_p = re.compile(colon_pattern)
import_parse_p = re.compile("Unable to import '(?P<module>[\w\.]+)'")


def parsed_lines(log_string):
    for line in log_string.split("\n"):
        m = line_parse_p.match(line)
        if m is not None:
            yield {k: v.strip() for k, v in m.groupdict().items()}


def missing_import_module(msg):
    return import_parse_p.match(msg).groupdict()["module"]


def process_parsed_line(parsed):
    if parsed["code"] == "E0401":
        package_name = missing_import_module(parsed["msg"]).split(".")[0]
        yield "missing_package", package_name
    elif parsed["code"] == "C0114":
        yield "missing_docstring", parsed["path"]


def analyze_log(log_string):
    from collections import defaultdict

    report = defaultdict(set)
    for parsed in parsed_lines(log_string):
        for kind, info in process_parsed_line(parsed):
            report[kind].add(info)

    return report


def _log_analysis_string_lines(log_string):
    report = analyze_log(log_string)
    for kind, info_set in report.items():
        yield f"---------- {kind} ----------\n"
        yield "\t" + "\n\t".join(info_set)
        yield "\n"


def log_analysis_string(log_string):
    return "".join(_log_analysis_string_lines(log_string))


def print_log_analysis(log_string):
    print(log_analysis_string(log_string))


def print_report_followed_by_log(log_string=None):
    if log_string is None:
        import sys

        log_string = sys.stdin.read()

    try:
        print(
            "\n------------------- SYNOPSIS --------------------\n\n"
            + log_analysis_string(log_string)
            + "\n\n---------------------- PYLINT LOGS -----------------------\n\n"
            + log_string
        )
    except Exception:
        # if there's any exception computing log_analysis_string, just print log_string
        print(log_string)


if __name__ == "__main__":
    import sys

    log_string = sys.stdin.read()
    print_report_followed_by_log(log_string)
