# This file implements manual integration tests and coverage computations.
# This is so that GitHub action results remain comprehensive and the respective
# test's developer can see that further action is needed.
#
# To run the tests, you need to install all module requirements with `pip install -r requirements[test].txt`
#
# After running the file locally, run  `coverage report` to see a console summary and `coverage html codecov`
# to generate interactive html for exploring tracked files from the `mammoth/` and `catalogue/` directories.
import os
import sys
from contextlib import redirect_stdout, redirect_stderr
import coverage

# some constants for pretty printing
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# need this as globals passed to execs
cov = coverage.Coverage(source=["mammoth", "catalogue"])
cov.start()


def run_test(file_path):
    try:
        with open(os.devnull, "w") as devnull, redirect_stdout(
            devnull
        ), redirect_stderr(devnull):
            with open(file_path, "r") as file:
                exec(file.read(), globals())
        print(f"{file_path.ljust(60)}: {GREEN}PASS{RESET}")
        return True
    except Exception as e:
        print(f"{file_path.ljust(60)}: {RED}FAILED{RESET} - {str(e)}")
        return False


def run_tests_in_folder(path):
    success = True
    for file_name in os.listdir(path):
        if file_name.endswith(".py") and file_name.startswith("test_"):
            file_path = os.path.join(path, file_name)
            success = (
                run_test(file_path) and success
            )  # careful of the order (run everything on failure too)
    return success


if __name__ == "__main__":
    # monkey patch mammoth classes for tests to run quietly
    import matplotlib
    from mammoth.exports import HTML, Markdown

    HTML.show = lambda self: self.text()
    Markdown.show = lambda self: self.text()
    matplotlib.use("Agg")  # disable window visualization

    # run the actual tests
    folder_path = "tests"
    if not run_tests_in_folder(folder_path):
        # cov.report()
        cov.stop()
        cov.save()
        sys.exit(1)  # fail github actions
    else:
        # cov.report()
        cov.stop()
        cov.save()
