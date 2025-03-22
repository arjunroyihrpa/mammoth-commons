import logging

logging.getLogger().setLevel(logging.ERROR)


try:
    from mai_bias import states
    from mai_bias import backend
    from mai_bias import bias
except ImportError:
    print(
        "Failed to import MAI-Bias frontend (you are probably lacking a graphics environment)"
    )
