class Dataset:
    integration = "dsl.Dataset"

    def to_features(self, sensitive):
        raise Exception(
            f"Dataset {self.__class__.__name__} has no way to retrieve features"
        )
