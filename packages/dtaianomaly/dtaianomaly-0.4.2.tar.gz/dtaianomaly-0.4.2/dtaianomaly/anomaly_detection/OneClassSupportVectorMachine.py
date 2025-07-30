from typing import Literal

from pyod.models.ocsvm import OCSVM

from dtaianomaly.anomaly_detection.BaseDetector import Supervision
from dtaianomaly.anomaly_detection.PyODAnomalyDetector import PyODAnomalyDetector


class OneClassSupportVectorMachine(PyODAnomalyDetector):
    """
    Anomaly detector based on One-Class Support Vector Machines (OC-SVM) :cite:`scholkopf1999support`.

    The OC-SVM uses a Support Vector Machine to learn
    a boundary around the normal behavior with minimal margin. New data can
    then be identified as anomaly or not, depending on if the data falls within
    this boundary (and thus is normal) or outside the boundary (and thus is
    anomalous).

    Parameters
    ----------
    window_size: int or str
        The window size to use for extracting sliding windows from the time series. This
        value will be passed to :py:meth:`~dtaianomaly.anomaly_detection.compute_window_size`.
    stride: int, default=1
        The stride, i.e., the step size for extracting sliding windows from the time series.
    kernel: {'linear', 'poly', 'rbf', 'sigmoid', 'cosine'}, default='rbf'
        The kernel to use for PCA.
    **kwargs:
        Arguments to be passed to the PyOD OC-SVM

    Attributes
    ----------
    window_size_: int
        The effectively used window size for this anomaly detector
    pyod_detector_ : OCSVM
        A OCSVM-detector of PyOD

    Examples
    --------
    >>> from dtaianomaly.anomaly_detection import OneClassSupportVectorMachine
    >>> from dtaianomaly.data import demonstration_time_series
    >>> x, y = demonstration_time_series()
    >>> ocsvm = OneClassSupportVectorMachine(10).fit(x)
    >>> ocsvm.decision_function(x)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    array([-0.7442125 , -1.57019847, -1.86868112, ..., 13.33883568, 12.6492399 , 11.8761641 ]...)

    Notes
    -----
    The OC-SVM inherets from :py:class:`~dtaianomaly.anomaly_detection.PyodAnomalyDetector`.
    """

    kernel: Literal["linear", "poly", "rbf", "sigmoid", "cosine"]

    def __init__(
        self,
        window_size: int | str,
        stride: int = 1,
        kernel: Literal["linear", "poly", "rbf", "sigmoid", "cosine"] = "rbf",
        **kwargs,
    ):
        if not isinstance(kernel, str):
            raise TypeError("`kernel` should be a string!")
        if kernel not in ["linear", "poly", "rbf", "sigmoid", "cosine"]:
            raise ValueError(
                "`kernel` should be one of {'linear', 'poly', 'rbf', 'sigmoid', 'cosine'}"
            )

        self.kernel = kernel

        super().__init__(window_size, stride, **kwargs)

    def _initialize_detector(self, **kwargs) -> OCSVM:
        return OCSVM(**kwargs)

    def _supervision(self):
        return Supervision.SEMI_SUPERVISED
