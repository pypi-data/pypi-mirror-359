import numpy as np

from dtaianomaly.anomaly_detection import BaseDetector
from dtaianomaly.preprocessing import ChainedPreprocessor, Preprocessor
from dtaianomaly.utils import is_valid_list


class Pipeline(BaseDetector):
    """
    Pipeline to combine preprocessing and anomaly detection

    The pipeline works with a single :py:class:`~dtaianomaly.preprocessing.Preprocessor` object or a
    list of :py:class:`~dtaianomaly.preprocessing.Preprocessor` objects. This list is converted into a
    :py:class:`~dtaianomaly.preprocessing.ChainedPreprocessor`. At the moment the `Pipeline` always
    requires a `Preprocessor` object passed at construction. If
    no preprocessing is desired, you need to explicitly pass an
    :py:class:`~dtaianomaly.preprocessing.Identity` preprocessor.

    Parameters
    ----------
    preprocessor: Preprocessor or list of Preprocessors
        The preprocessors to include in this pipeline.
    detector: BaseDetector
        The anomaly detector to include in this pipeline.
    """

    preprocessor: Preprocessor
    detector: BaseDetector

    def __init__(
        self,
        preprocessor: Preprocessor | list[Preprocessor],
        detector: BaseDetector,
    ):
        if not (
            isinstance(preprocessor, Preprocessor)
            or is_valid_list(preprocessor, Preprocessor)
        ):
            raise TypeError(
                "preprocessor expects a Preprocessor object or list of Preprocessors"
            )
        if not isinstance(detector, BaseDetector):
            raise TypeError("detector expects a BaseDetector object")
        super().__init__(detector.supervision)

        if isinstance(preprocessor, list):
            self.preprocessor = ChainedPreprocessor(preprocessor)
        else:
            self.preprocessor = preprocessor
        self.detector = detector

    def _fit(self, X: np.ndarray, y: np.ndarray = None, **kwargs) -> None:
        X, y = self.preprocessor.fit_transform(X=X, y=y)
        self.detector.fit(X=X, y=y, **kwargs)

    def _decision_function(self, X: np.ndarray) -> np.array:
        X, _ = self.preprocessor.transform(X=X, y=None)
        return self.detector.decision_function(X)

    def __str__(self) -> str:
        return f"{self.preprocessor}->{self.detector}"
