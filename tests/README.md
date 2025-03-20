# MAMMOth Integration Tests

This directory contains test pipelines of modules
by implementing MAMMOth's technical components.
If you just cloned this repository, install the
`mammoth` namespace in development mode from the top
level (you should never need to navigate within
this directory) per:

```bash
pip install -e .
```

All tests comprise the context `with testing.Env(...) as env:`
to convert modules back into Python methods. Modules are called
normally by passing keyword arguments, where additionally
metric modules require the output of model loaders and dataset
loaders. The final results of metrics, be they in markdown
or html formats can be opened in the browser
with the `.show()` method.

You might need to install additional dependencies (that would
be automatically handled by docker in production) to run tests.
Find the needed dependencies on module declarations as the `packages`
field. For example, to run the test of TC1 install the dependencies
of `catalogue.dataset_loaders.images.data_images`,  
`catalogue.model_loaders.pytorch.model_torch`,
`catalogue.metrics.image_bias_analysis.image_bias_analysis`
and then run the test with Python per:

```bash
pip install torch, torchvision, cvbiasmitigation
python .\tests\test_tc1_bias_mitigation_cv.py
```

:bulb: You can view a summary of modules and dependencies [here](../catalogue/README.md).
