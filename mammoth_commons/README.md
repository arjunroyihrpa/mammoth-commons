#  MAMMOth-commons

This directory hosts the source code of the MAMMOth-commons package.
That is, import statements from the package, like 
`from mammoth_commons.models import ONNX`, access the contents of this directory.

The current structure into subdirectories corresponding to Python modules is as follows:

| Subdirectory/File | Description                                                                                                                                                            |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `datasets/`       | Dataset **types** that are the outcomes of dataset loader module and serve as inputs to metric modules.                                                                |
| `models/`         | Model **types** that are the outcomes of model loader modules and serve as inputs to metric modules.                                                                   |
| `integration.py`  | Implementation of decorators that create and actually decorate normal kfp methods.                                                                                     |
| `custom_kfp.py`   | A modification of some kfp functionality to make it compatible withall interfaces.                                                                                     |
| `testing.py`      | Implementation of functionality to strip away the decorators from the kfp integration process, and therefore allow unit and integration tests of developed components. |
| `externals.py`    | Supporting methods for module creation, for example that automate safe running of third-party code.                                                                    |

:warning: Contributions will be accepted only for the `datasets/` and `models/` directories. 
The rest need some knowledge of the MIA-BIAS toolkit's common internal workings across
all platforms to properly understand.
Furthermore, make sure that libraries other than those in `requirements.txt` (**not** the text with 
[all] requirements) are imported from within functions. The canary test in GitHub actions tests
for this scenario. Replicate it locally to assert that you have not mistakenly added an import.
