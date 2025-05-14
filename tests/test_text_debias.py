import shutil
import zipfile
import site
from urllib.request import urlretrieve
import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
try:
    from Dbias.text_debiasing import *
    from Dbias.bias_classification import *
    from Dbias.bias_recognition import *
    from Dbias.bias_masking import *
except:

    def manual_install_wheel(wheel_url_or_path):
        print("Manually installing a broken wheel for the DBias library")
        if wheel_url_or_path.startswith("http://") or wheel_url_or_path.startswith(
            "https://"
        ):
            local_whl = os.path.join(".cache", os.path.basename(wheel_url_or_path))
            print(f"Downloading wheel from {wheel_url_or_path}...")
            urlretrieve(wheel_url_or_path, local_whl)
        else:
            local_whl = wheel_url_or_path
            if not os.path.exists(local_whl):
                raise FileNotFoundError(f"No such file: {local_whl}")
        print(f"Unpacking {local_whl}...")
        unpack_dir = local_whl.replace(".whl", "_unpacked")
        with zipfile.ZipFile(local_whl, "r") as zf:
            zf.extractall(unpack_dir)
        site_packages_dirs = site.getsitepackages()
        if not site_packages_dirs:
            site_packages_dirs = [site.getusersitepackages()]
        site_packages = site_packages_dirs[0]
        print(f"Copying to site-packages at: {site_packages}")
        for item in os.listdir(unpack_dir):
            src_path = os.path.join(unpack_dir, item)
            dst_path = os.path.join(site_packages, item)
            if os.path.exists(dst_path):
                print(f"Overwriting existing: {dst_path}")
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                else:
                    os.remove(dst_path)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        print(f"Installed {local_whl} manually into site-packages.")

    manual_install_wheel(
        "https://huggingface.co/d4data/en_pipeline/resolve/main/en_pipeline-any-py3-none-any.whl"
    )


from Dbias.text_debiasing import *
from Dbias.bias_classification import *
from Dbias.bias_recognition import *
from Dbias.bias_masking import *

"""
<p>
This module uses <a href="https://github.com/dreji18/Fairness-in-AI">DBias</a> library to perform
unsupervised auditing of text biases in text resembling article titles. If library identifies biases, it is used to 
mitigate them with a more neutral phrasing. Results show a judgement and prediction confidence for the original
and adjusted text, as well as potentially offending keywords.
</p>

<p>
The DBias library employs three transformer models,
one pretrained for the English language and two trained 
on the <a href="https://github.com/Media-Bias-Group/Neural-Media-Bias-Detection-Using-Distant-Supervision-With-BABE">MBIC dataset</a>.
</p>
"""


text = "Billie Eilish issues apology for mouthing an anti-Asian derogatory term in a resurfaced video."


def custom_debiasing(x):
    suggestions = run(x)
    if suggestions is None:
        return ""
    all_suggestions = []
    for sent in suggestions[0:3]:
        all_suggestions.append(sent["Sentence"])
    return "\n\n".join(all_suggestions)


def custom_recognizer(x):
    biased_words = recognizer(x)
    biased_words_list = []
    for id in range(0, len(biased_words)):
        biased_words_list.append(biased_words[id]["entity"])
    return ", ".join(biased_words_list)


print(classify(text))
print(custom_recognizer(text))
print(custom_debiasing(text))
