from pathlib import Path
import os


def get_import_list(code):
    code = Path(code).read_text() if code.endswith(".py") else code
    found_imports = list()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            imported_modules = line.split("import", 1)[1].strip().split(",")
            for module in imported_modules:
                module_name = module.split()[0].split(".")[0].strip()
                found_imports.append(module_name)
        elif line.startswith("from "):
            parts = line.split()
            if len(parts) > 1:
                module_name = parts[1].split(".")[0]
                found_imports.append(module_name)
    return found_imports


def safeexec(code: str, out: str = "commons", whitelist: list[str] = None):
    code = Path(code).read_text() if code.endswith(".py") else code
    whitelist = () if whitelist is None else set(whitelist)
    for module_name in get_import_list(code):
        assert (
            module_name in whitelist
        ), f"Disallowed import detected: '{module_name}'. Only these are allowed: {','.join(whitelist)}"
    exec_context = locals().copy()
    exec(code, exec_context)
    assert (
        out in exec_context
    ), f"The provided script or file did not contain an {out} variable"
    return exec_context[out]


def get_model_layer_list(model):
    try:
        model = model.model
        return [name for name, _ in model.named_modules() if name]
    except Exception as e:
        print(e)
        return []


def align_predictions_labels(predictions, labels):
    if isinstance(labels, dict) and len(labels) == 1:
        labels = labels[next(labels.keys().__iter__())]

    if labels is not None and hasattr(labels, "columns") and len(labels.columns) == 1:
        labels = labels[labels.columns[0]]

    if labels is not None and hasattr(labels, "columns"):
        labels = {col: labels[col] for col in labels.columns}

    if (
        labels is not None
        and not isinstance(predictions, dict)
        and isinstance(labels, dict)
    ):
        if "0" in labels and "1" in labels and len(labels) == 2:
            predictions = {"0": 1 - predictions, "1": predictions}
        elif "no" in labels and "yes" in labels and len(labels) == 2:
            predictions = {"no": 1 - predictions, "yes": predictions}
        else:
            raise Exception(
                f"The selected model creates a vector of predictions but it is unknown how to match this to multiple labels {','.join(labels.keys())}. Make the dataset have 0/1 or no/yes labels to automatically convert the prediction to two columns."
            )

    if (
        labels is not None
        and isinstance(labels, dict)
        and isinstance(predictions, dict)
    ):
        predictions = {f"class {k}": v for k, v in predictions.items()}
        labels = {f"class {k}": v for k, v in labels.items()}

    return predictions, labels


def fb_categories(it):
    import fairbench as fb

    @fb.v1.Transform
    def categories(iterable):
        is_numeric = True
        values = list()
        for value in iterable:
            try:
                values.append(float(value))
            except Exception:
                is_numeric = False
                break
        # if len(set(v for v in values)) == 2:
        #    is_numeric = False
        if is_numeric:
            values = fb.v1.tobackend(values)
            mx = values.max()
            mn = values.min()
            if mx == mn:
                mx += 1
            values = fb.v1.tobackend((values - mn) / (mx - mn))
            return {
                f"fuzzy min ({mn:.3f})": 1 - values,
                f"fuzzy max ({mx:.3f})": values,
            }
        return fb.categories @ iterable

    return categories @ it


def _download(url, path=None):
    import urllib.request
    import os

    # Get the file name from the URL
    if path is None:
        file_name = os.path.basename(url)
    else:
        file_name = path

    try:
        with urllib.request.urlopen(url) as response:
            total_size = response.getheader("Content-Length")
            total_size = int(total_size) if total_size else None

            with open(file_name, "wb") as out_file:
                chunk_size = 1024
                downloaded = 0

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)

                    # Print progress if total size is known
                    if total_size:
                        done = int(50 * downloaded / total_size)
                        print(
                            f'\rDownloading {url} [{"=" * done}{" " * (50 - done)}] {downloaded / 1024:.2f} KB',
                            end="",
                        )

        print(f"Downloaded {url}" + " " * 50)
    except Exception as e:
        print(f"Error downloading file: {e}")


def _extract_nested_zip(file, folder):
    import zipfile

    os.makedirs(folder, exist_ok=True)
    with zipfile.ZipFile(file, "r") as zfile:
        zfile.extractall(path=folder)
    os.remove(file)
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".zip"):
                _extract_nested_zip(
                    os.path.join(root, filename), os.path.join(root, filename[:-4])
                )


def pd_read_csv(url, **kwargs):
    import pandas as pd
    import csv

    url = url.replace("\\", "/")
    if ".zip/" in url:
        url, path = url.split(".zip/", 1)
        extract_to = "data/"
        if "/" not in path:
            extract_to += url.split("/")[-1]
            path = os.path.join(url.split("/")[-1], path)
        path = os.path.join("data", path)
        url += ".zip"
        temp = "data/" + url.split("/")[-1]
        if not os.path.exists(path):
            os.makedirs(os.path.join(*path.split("/")[:-1]), exist_ok=True)
            _download(url, temp)
            _extract_nested_zip(temp, extract_to)
    elif os.path.exists(url):  # or url.startswith("http:") or url.startswith("https:"):
        path = url
    else:
        shortened = "/".join(url.split("/")[-4:])  # TODO: be more clever here
        path = "data/" + shortened
        if not os.path.exists(path):
            os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
            _download(url, path)

    if path.endswith("bz2"):
        import bz2

        with bz2.BZ2File(path, "rb") as bz2_file:
            with open(path[:-4], "wb") as out_file:
                out_file.write(bz2_file.read())
        path = path[:-4]

    if "delimiter" in kwargs:
        return pd.read_csv(path, **kwargs)

    with open(path, "r") as file:
        sample = file.read(1024)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        delimiter = str(delimiter)
    return pd.read_csv(path, delimiter=delimiter, **kwargs)
