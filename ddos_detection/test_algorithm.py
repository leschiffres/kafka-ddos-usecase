from unittest.mock import patch
from ddos_detection.algorithm import alon_matias_szegedy_mmd, baseline_instance
import numpy as np


def test_alon_matias_szegedy_mmd():
    with patch('numpy.random.randint') as mock_randomization:
        """
        with this test we reproduce the example found in the mining massive datasets book
        and make sure we get the same value
        """
        mock_randomization.return_value = np.array([2, 7, 12])
        stream = baseline_instance()
        estimator = alon_matias_szegedy_mmd(stream, passes=3)
        assert estimator == 55
