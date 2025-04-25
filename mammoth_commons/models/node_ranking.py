from mammoth_commons.models.predictor import Predictor


class NodeRanking(Predictor):
    def __init__(self, diffusion: float = 0.9, redistribution: str = "none"):
        self.redistribution = redistribution
        self.params = {"alpha": diffusion, "tol": 1.0e-9, "max_iters": 3000}

    def _run(self, x, **kwargs):
        import pygrank as pg

        ranker = (
            pg.PageRank(**self.params)
            if self.redistribution == "none"
            else pg.LFPR(redistributor=self.redistribution, **self.params)
        )
        ranker >> pg.Normalize("max")
        return ranker(x, **kwargs)

    def predict_unfair(self, x):
        import networkx as nx
        import pygrank as pg

        assert isinstance(x, nx.Graph) or isinstance(x, pg.Graph)
        return self._run(x)

    def predict(self, dataset, sensitive):
        assert (
            len(sensitive) == 1
        ), "fair node ranking algorithms can only account for one sensitive attribute"
        import networkx as nx
        import pygrank as pg

        x = dataset.to_features(None)
        sensitive = dataset.to_features(sensitive)
        assert isinstance(x, nx.Graph) or isinstance(x, pg.Graph)
        return self._run(x, sensitive=sensitive[0]).np
