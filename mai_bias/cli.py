import json
import os
import re
import readchar
from datetime import datetime
from mai_bias.backend.loaders import registry

tags = {
    key: "<h1>" + key + "</h1>" + module["description"]
    for key, module in (
        registry.dataset_loaders | registry.model_loaders | registry.analysis_methods
    ).items()
}


def now():
    return datetime.now().strftime("%y-%m-%d %H:%M")


def save_all_runs(path, runs):
    copy_runs = list()
    for run in runs:
        copy_run = dict()
        copy_run["timestamp"] = run["timestamp"]
        copy_run["description"] = run["description"]
        copy_run["status"] = run.get("status", None)
        if "dataset" in run:
            copy_run["dataset"] = {
                "module": run["dataset"]["module"],
                "params": run["dataset"]["params"],
            }
        if "model" in run:
            copy_run["model"] = {
                "module": run["model"]["module"],
                "params": run["model"]["params"],
            }
        if "analysis" in run:
            copy_run["analysis"] = {
                "module": run["analysis"]["module"],
                "params": run["analysis"]["params"],
                "return": run["analysis"].get("return", None),
            }
        copy_runs.append(copy_run)
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(copy_runs))


def load_all_runs(path):
    if not os.path.exists(path):
        return list()
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def format_name(name):
    """Format parameter names for better display."""
    return name.replace("_", " ").capitalize()


def extract_title(run):
    try:
        match = re.search(
            r"<h1\b[^>]*>.*?</h1>",
            run.get("analysis", dict()).get("return", ""),
            re.DOTALL,
        )
        if match:
            return match.group().replace("h1", "span")
    except Exception:
        pass
    return ""


class colorsbg:
    fail = "\033[41m"
    ok = "\033[42m"
    warn = "\033[43m"
    element = "\033[44m"
    # neutral = "\033[45m"
    neutral = "\033[100m"


class colors:
    reset = "\033[0m"
    fail = "\033[31m"
    ok = "\033[32m"
    warn = "\033[33m"
    element = "\033[34m"
    # neutral = "\033[35m"
    neutral = "\033[0m"


class Preview:
    def __init__(self, results, base_state, title):
        self.base_state = base_state
        self.title = title
        self.selection = 0
        self.base_state = base_state
        self.unhandled_button = None
        self.modifying_pos = 0
        self.modifying = False
        self.next = self
        self.title = title
        self.runs = runs
        self.height = 15
        import html2text
        from rich.console import Console
        from rich.markdown import Markdown

        results = html2text.html2text(results)
        console = Console()
        with console.capture() as capture:
            console.print(Markdown(results), width=80)
        self.results = capture.get().split("\n")

    def show(self):
        print("\x1b[2J\x1b[H")
        print(self.title)
        print("─" * 80)
        print(colorsbg.fail + f"Close".ljust(80) + colors.reset)
        print("─" * 80)

        if self.selection >= len(self.results) - self.height:
            self.selection = len(self.results) - self.height
        if self.selection < 0:
            self.selection = 0
        selection_end = min(len(self.results), self.selection + self.height)
        results = self.results[self.selection : selection_end]
        print("\n".join(results))
        print("─" * 80)

        if self.modifying:
            self.modifying = False
            self.next = self.base_state
            self.next.next = self.next


class Select:
    def __init__(self, options, base_state, title=None, runs=None, reference=None):
        self.selection = 0
        self.base_state = base_state
        self.unhandled_button = None
        self.options = options
        self.modifying_pos = 0
        self.modifying = False
        self.next = self
        self.title = title
        self.runs = runs
        self.reference = reference

    def show(self):
        if self.selection < 0:
            self.selection = 0
        if self.selection >= len(self.options):
            self.selection = len(self.options) - 1
        if self.title:
            print("\x1b[2J\x1b[H")
            print(self.title)
            print("─" * 80)
        else:
            self.base_state.show()
        for i, option in enumerate(self.options):
            coloring = colorsbg if i == state.selection else colors
            print(f"{option[0](coloring)}{colors.reset}")
        print("─" * 80)

        if self.modifying:
            self.modifying = False
            for i, option in enumerate(self.options):
                if i == state.selection:
                    getattr(self, option[1])()

    def data_loader(self):
        run = self.runs[self.reference]
        results = run.get("dataset", dict()).get("module", "No data loader")
        self.next = Preview(
            tags[results] if results in tags else "No description available.",
            self,
            colors.warn + "Info: " + results + colors.reset,
        )

    def model_loader(self):
        run = self.runs[self.reference]
        results = run.get("model", dict()).get("module", "No model loader")
        self.next = Preview(
            tags[results] if results in tags else "No description available.",
            self,
            colors.warn + "Info: " + results + colors.reset,
        )

    def analysis_method(self):
        run = self.runs[self.reference]
        results = run.get("analysis", dict()).get("module", "No analysis method")
        self.next = Preview(
            tags[results] if results in tags else "No description available.",
            self,
            colors.warn + "Info: " + results + colors.reset,
        )

    def results(self):
        run = self.runs[self.reference]
        results = run.get("analysis", dict()).get("return", "No results available.")
        self.next = Preview(results, self, self.title)

    def html(self):
        run = self.runs[self.reference]
        results = run.get("analysis", dict()).get("return", "No results available.")
        with open("temp.html", "w", encoding="utf-8") as file:
            file.write(results)
        print(colors.ok + f"Saved as temp.html".rjust(78) + colors.reset)
        try:
            import webbrowser

            webbrowser.open_new("temp.html")
            print(
                colors.ok + f"Opened temp.html in the browser".rjust(78) + colors.reset
            )
        except Exception as e:
            print(
                colors.fail
                + f"Failed to open the browser: {str(e)}".rjust(78)
                + colors.reset
            )

    def cancel(self):
        self.next = self.base_state
        self.next.next = self.next

    def delete(self):
        del self.runs[self.reference]
        self.cancel()

    def edit(self):
        run = self.runs[self.reference]
        loaders = [loader for loader, values in registry.dataset_loaders.items()]
        self.next = Step(
            loaders,
            self,
            colors.warn + "1/3 Dataset loader" + colors.reset,
            run,
        )


class Step:
    def __init__(self, modules, base_state, title, run, module_discovery="dataset"):
        self.base_state = base_state
        self.selection = -1
        self.modifying = False
        self.modifying_pos = 0
        self.run = run
        self.next = self
        self.title = title
        self.unhandled_button = None
        self.inputs = list()
        self.modules = modules
        self.selected_module = 0
        self.input_character = ""
        self.module_discovery = module_discovery
        for i, module in enumerate(modules):
            if module == run.get(module_discovery, dict()).get("module", ""):
                self.next.selected_module = i

    def cancel(self):
        self.next = self.base_state
        self.next.next = self.next

    def show(self):

        print("\x1b[2J\x1b[H")
        print(self.title)
        print("─" * 80)

        module_name = self.modules[self.selected_module]
        module = registry.dataset_loaders[module_name]

        if self.selection < -2:
            self.selection = -2

        if self.selection == -1:
            self.selected_module += self.modifying_pos
            if self.selected_module < 0:
                self.selected_module = len(self.modules) - 1
            if self.selected_module >= len(self.modules):
                self.selected_module = 0

            module_name = self.modules[self.selected_module]
            module = registry.dataset_loaders[module_name]
            if self.module_discovery in self.run:
                self.run[self.module_discovery]["module"] = module_name

            if self.modifying:
                self.modifying = False
                self.next = Preview(
                    (
                        tags[module_name]
                        if module_name in tags
                        else "No description available."
                    ),
                    self,
                    colors.warn
                    + "Info: "
                    + format_name(module_name)
                    + ""
                    + colors.reset
                    + "\nThis appeared because you pressed [enter] during module selection."
                    + "\nUse left/right arrows to change the selection.",
                )
        elif self.selection == -2 and self.modifying:
            self.cancel()
        else:
            if self.selection >= len(module["parameters"]):
                self.selection = len(module["parameters"]) - 1

        coloring = colorsbg if -2 == state.selection else colors
        print(f"{coloring.warn}{'Cancel'.ljust(80)}{colors.reset}")
        coloring = colorsbg if -1 == self.selection else colors
        print(
            f"{coloring.element}{'Loader'.ljust(30)} {"← "+format_name(module_name).center(44)+" → "}{colors.reset}"
        )

        if "dataset" not in self.run:
            self.run["dataset"] = {"module": module_name, "params": dict()}
        i = 0
        for name, param_type, default, description in module["parameters"]:
            if self.modifying and i == self.selection:
                self.modifying = False
                self.next = Preview(
                    description,
                    self,
                    colors.warn
                    + "Info: "
                    + format_name(name)
                    + ""
                    + colors.reset
                    + "\nThis appeared because you pressed [enter] during parameter selection."
                    + "\nUse left/right arrows, [tab] for autocomplete, or type to modify the parameter.",
                )

            coloring = colorsbg if i == self.selection else colors
            if name not in self.run["dataset"]["params"]:
                self.run["dataset"]["params"][name] = (
                    "" if default is None or default == "None" else str(default)
                )
            if self.input_character == readchar.key.BACKSPACE:
                self.run["dataset"]["params"][name] = self.run["dataset"]["params"][
                    name
                ][:-1]
            if (
                i == self.selection
                and len(self.input_character) == 1
                and self.input_character.isprintable()
            ):
                self.run["dataset"]["params"][name] += self.input_character

            if param_type == "bool":
                if self.modifying_pos != 0 and i == self.selection:
                    self.run["dataset"]["params"][name] = (
                        "True"
                        if self.run["dataset"]["params"][name] == "False"
                        else "False"
                    )
                print(
                    f"{coloring.neutral}{format_name(name).ljust(30)} {"← "+self.run["dataset"]["params"][name].center(44)+" → "}{colors.reset}"
                )
            else:
                print(
                    f'{coloring.neutral}{format_name(name).ljust(30)} {self.run["dataset"]["params"][name].ljust(49)}{colors.reset}'
                )
            # print(param_type)
            i += 1
        print("─" * 80)

        self.modifying_pos = 0
        self.input_character = ""


class Dashboard:
    def __init__(self, runs):
        self.selection = -1
        self.modifying = False
        self.modifying_pos = 0
        self.runs = runs
        self.next = self
        self.unhandled_button = None

    def show(state):
        runs = state.runs
        print("\x1b[2J\x1b[H")
        print(f"\033[1m{colors.warn}MAI-BIAS command line\033[0m")
        print("─" * 80)
        if state.selection < -2:
            state.selection = -2
        if state.selection >= len(runs):
            state.selection = len(runs) - 1
        coloring = colorsbg if -2 == state.selection else colors
        print(f"{coloring.fail}{'Exit'.ljust(80)}{colors.reset}")
        coloring = colorsbg if -1 == state.selection else colors
        print(f"{coloring.element}{'New run'.ljust(80)}{colors.reset}")
        for i, run in enumerate(runs):
            description = run["description"]
            if not description:
                description = "..."
            description = description.ljust(20)
            title = extract_title(run)
            title = title.replace("<span>", "").replace("</span>", "").ljust(40)
            time = run.get("timestamp", "").ljust(18)
            coloring = colorsbg if i == state.selection else colors
            button_color = (
                (
                    coloring.fail
                    if "fail" in title or "bias" in title
                    else (
                        coloring.ok
                        if "report" in title
                        or "audit" in title
                        or "scan" in title
                        or "analysis" in title
                        or "explanation" in title
                        else coloring.neutral
                    )
                )
                if run["status"] == "completed"
                else coloring.warn
            )
            print(f"{button_color}{description} {time} {title}{colors.reset}")
        print("─" * 80)
        if state.modifying:
            state.modifying = False
            if state.selection == -2:
                state.next = None
            elif state.selection == -1:
                state.runs.append(
                    {"description": "", "timestamp": now(), "status": "in_progress"}
                )
                loaders = [
                    loader for loader, values in registry.dataset_loaders.items()
                ]
                state.next = Step(
                    loaders,
                    state,
                    colors.warn + "1/3 Dataset loader" + colors.reset,
                    state.runs[-1],
                )
            else:
                run = runs[state.selection]
                description = run["description"]
                if not description:
                    description = "..."
                description = description.ljust(20)
                title = extract_title(run)
                title = title.replace("<span>", "").replace("</span>", "").ljust(40)
                time = run.get("timestamp", "").ljust(18)

                select = Select(
                    [
                        (
                            lambda col: getattr(col, "warn") + "Cancel".ljust(80),
                            "cancel",
                        ),
                        (
                            lambda col: getattr(col, "element")
                            + "Console preview".ljust(80),
                            "results",
                        ),
                        (
                            lambda col: getattr(col, "element") + "Show html".ljust(80),
                            "html",
                        ),
                        (
                            lambda col: getattr(col, "element")
                            + "New variation".ljust(80),
                            "variation",
                        ),
                        (
                            lambda col: getattr(col, "neutral")
                            + f"Info: {run.get("dataset", dict()).get("module", "No data loader")}".ljust(
                                80
                            ),
                            "data_loader",
                        ),
                        (
                            lambda col: getattr(col, "neutral")
                            + f"Info: {run.get("model", dict()).get("module", "No model loader")}".ljust(
                                80
                            ),
                            "model_loader",
                        ),
                        (
                            lambda col: getattr(col, "neutral")
                            + f"Info: {run.get("analysis", dict()).get("module", "No analysis method")}".ljust(
                                80
                            ),
                            "analysis_method",
                        ),
                        (
                            lambda col: getattr(col, "fail")
                            + "Edit (loses results)".ljust(80),
                            "edit",
                        ),
                        (
                            lambda col: getattr(col, "fail") + "Delete".ljust(80),
                            "delete",
                        ),
                    ],
                    state,
                    f"{colors.warn}{description} {time} {title}{colors.reset}",
                    state.runs,
                    state.selection,
                )
                state.next = select


if __name__ == "__main__":
    runs = load_all_runs("history.json")
    state = Dashboard(runs)
    state.show()
    print("Use arrows to navigate, page up/down is faster, [enter] to select".rjust(78))
    while state is not None:
        c = readchar.readkey()
        if c == readchar.key.UP:
            state.selection -= 1
        elif c == readchar.key.DOWN:
            state.selection += 1
        elif c == readchar.key.PAGE_UP:
            state.selection -= 5
        elif c == readchar.key.PAGE_DOWN:
            state.selection += 5
        elif c == readchar.key.LEFT:
            state.modifying_pos -= 1
        elif c == readchar.key.RIGHT:
            state.modifying_pos += 1
        elif c == readchar.key.ENTER:
            state.modifying = not state.modifying
        else:
            state.input_character = str(c)
        state.show()
        while state is not None and state != state.next:
            state = state.next
            if state is not None:
                state.show()
        if state is None:
            print("Exiting...".rjust(78))
        else:
            print(
                "Use arrows to navigate, page up/down is faster, [enter] to select".rjust(
                    78
                )
            )
