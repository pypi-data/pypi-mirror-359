"""Explicit Kraskov-Stoegbauer-Grassberger mutual information estimator tests."""

import pytest
from numpy import linspace, inf, ndarray

from infomeasure.estimators.mutual_information import KSGMIEstimator, KSGCMIEstimator
from tests.conftest import generate_autoregressive_series_condition


@pytest.mark.parametrize(
    "data_x,data_y,k,minkowski_p,expected",
    [
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 1, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 2, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 3, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 1, 2, -0.85),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 2, 2, -0.1833333),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 3, 2, -0.4833333),
        ([1.0, 1.25, 0.91, 1.13, 1.32], [1.3, 1.1, 0.9, 1.2, 1.0], 1, inf, -0.5833333),
        ([1.01, 1.23, 0.92, 1.14, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 2, inf, -0.1833333),
        ([1.04, 1.23, 0.92, 1.1, 1.34], [1.3, 1.1, 0.9, 1.2, 1.0], 3, inf, -0.2833333),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 1, 1.6171394224015256),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 2, 2.828044184306288),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 3, 2.8360441843062887),
        (linspace(0, 1, 100), linspace(0, 1, 100), 1, 2, 2.1973775176396204),
        (linspace(0, 1, 100), linspace(0, 1, 100), 2, 2, 3.177377517639621),
        (linspace(0, 1, 100), linspace(0, 1, 100), 3, 2, 2.520710850972955),
        (linspace(0, 1, 100), linspace(1, 0, 100), 3, 2, 2.520710850972955),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [-8.59, 8.41, 3.76, 3.77, 5.69, 1.75, -3.2, -4.0, -4.0, 6.85],
            4,
            inf,
            -0.22710317460317464,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [11.08, 8.41, 11.47, 8.78, 14.09, 6.03, 10.67, 9.45, 12.72, 11.12],
            4,
            inf,
            -0.12253968253968255,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            4,
            inf,
            0.49563492063492054,
        ),
        (
            [0.32, -0.89, -0.01, 1.56, 0.24, 1.78, -1.63, 0.82, 0.12, 2.29],
            [0.22, -0.99, -0.11, 1.46, 0.14, 1.68, -1.73, 0.72, 0.02, 2.19],
            4,
            inf,
            0.49563492063492054,
        ),
        (
            [1.8, 1.1, 1.8, 1.1, 1.8, -2.0, 1.1, 1.8, -2.0, 1.1],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            4,
            inf,
            -0.4801587301587301,
        ),
    ],
)
def test_ksg_mi(data_x, data_y, k, minkowski_p, expected):
    """Test the Kraskov-Stoegbauer-Grassberger mutual information estimator."""
    est = KSGMIEstimator(
        data_x,
        data_y,
        k=k,
        minkowski_p=minkowski_p,
        noise_level=0,  # for reproducibility
    )
    assert isinstance(est.result(), float)
    assert est.result() == pytest.approx(expected)
    assert isinstance(est.local_vals(), ndarray)


@pytest.mark.parametrize(
    "data_x,data_y,k,minkowski_p,base,expected",
    [
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 3, 2, -0.36067376),
        (
            [1.04, 1.23, 0.92, 1.1, 1.34],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            3,
            inf,
            2,
            -0.40876359,
        ),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 3, 2, 4.0915468),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [-8.59, 8.41, 3.76, 3.77, 5.69, 1.75, -3.2, -4.0, -4.0, 6.85],
            4,
            inf,
            2,
            -0.3276406,
        ),
    ],
)
def test_ksg_mi_base(data_x, data_y, k, minkowski_p, base, expected):
    """Test the Kraskov-Stoegbauer-Grassberger mutual information estimator with a
    different base."""
    est = KSGMIEstimator(
        data_x,
        data_y,
        k=k,
        minkowski_p=minkowski_p,
        noise_level=0,  # for reproducibility
        base=base,
    )
    assert isinstance(est.result(), float)
    assert est.result() == pytest.approx(expected)
    assert isinstance(est.local_vals(), ndarray)


@pytest.mark.parametrize(
    "data_x,data_y,k,minkowski_p,expected",
    [
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 1, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 2, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 4, 3, -0.25),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 1, 2, -0.85),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 2, 2, -0.1833333),
        ([1.0, 1.2, 0.9, 1.1, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 3, 2, -0.4833333),
        ([1.0, 1.25, 0.91, 1.13, 1.32], [1.3, 1.1, 0.9, 1.2, 1.0], 1, inf, -0.5833333),
        ([1.01, 1.23, 0.92, 1.14, 1.3], [1.3, 1.1, 0.9, 1.2, 1.0], 2, inf, -0.1833333),
        ([1.04, 1.23, 0.92, 1.1, 1.34], [1.3, 1.1, 0.9, 1.2, 1.0], 3, inf, -1 / 3),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 1, 1.6171394224015256),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 2, 2.828044184306288),
        (linspace(0, 1, 100), linspace(0, 1, 100), 4, 3, 2.8360441843062887),
        (linspace(0, 1, 100), linspace(0, 1, 100), 1, 2, 2.1973775176396204),
        (linspace(0, 1, 100), linspace(0, 1, 100), 2, 2, 3.177377517639621),
        (linspace(0, 1, 100), linspace(0, 1, 100), 3, 2, 2.520710850972955),
        (linspace(0, 1, 100), linspace(1, 0, 100), 3, 2, 2.520710850972955),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [-8.59, 8.41, 3.76, 3.77, 5.69, 1.75, -3.2, -4.0, -4.0, 6.85],
            4,
            inf,
            -0.24710317460317466,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [11.08, 8.41, 11.47, 8.78, 14.09, 6.03, 10.67, 9.45, 12.72, 11.12],
            4,
            inf,
            0.015595238095237995,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            4,
            inf,
            0.49563492063492054,
        ),
        (
            [0.32, -0.89, -0.01, 1.56, 0.24, 1.78, -1.63, 0.82, 0.12, 2.29],
            [0.22, -0.99, -0.11, 1.46, 0.14, 1.68, -1.73, 0.72, 0.02, 2.19],
            4,
            inf,
            0.49563492063492054,
        ),
        (
            [1.8, 1.1, 1.8, 1.1, 1.8, -2.0, 1.1, 1.8, -2.0, 1.1],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            4,
            inf,
            -0.5347222222222221,
        ),
    ],
)
def test_ksg_mi_normalized(data_x, data_y, k, minkowski_p, expected):
    """
    Test the Kraskov-Stoegbauer-Grassberger mutual information estimator with normalization.
    """
    est = KSGMIEstimator(
        data_x,
        data_y,
        k=k,
        minkowski_p=minkowski_p,
        noise_level=0,  # for reproducibility
        normalize=True,
    )
    assert isinstance(est.result(), float)
    assert est.result() == pytest.approx(expected)
    assert isinstance(est.local_vals(), ndarray)


@pytest.mark.parametrize(
    "data_x,data_y,cond,k,minkowski_p,base,expected",
    [
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            4,
            1,
            "e",
            -0.25,
        ),
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            4,
            2,
            "e",
            -0.25,
        ),
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            4,
            3,
            "e",
            -0.25,
        ),
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            1,
            2,
            "e",
            -1.13333333333,
        ),
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            2,
            2,
            "e",
            -0.699999999999,
        ),
        (
            [1.0, 1.2, 0.9, 1.1, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            3,
            2,
            "e",
            -0.4833333,
        ),
        (
            [1.0, 1.25, 0.91, 1.13, 1.32],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            1,
            inf,
            "e",
            -0.81666666,
        ),
        (
            [1.01, 1.23, 0.92, 1.14, 1.3],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            2,
            inf,
            "e",
            -0.533333333,
        ),
        (
            [1.04, 1.23, 0.92, 1.1, 1.34],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            3,
            inf,
            "e",
            -1 / 3,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            4,
            1,
            "e",
            0.1326551226,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            4,
            2,
            "e",
            0.11333333333,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            4,
            3,
            "e",
            -0.242,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            1,
            2,
            "e",
            -1.49,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            2,
            2,
            "e",
            -0.493333333,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            3,
            2,
            "e",
            -0.210666666,
        ),
        (
            linspace(0, 1, 100),
            linspace(0, 1, 100),
            linspace(1, 0, 100),
            3,
            2,
            "e",
            -0.210666666,
        ),
        (
            linspace(0, 1, 100),
            linspace(1, 0, 100),
            linspace(1, 0, 100),
            3,
            2,
            "e",
            -0.210666666,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [7.95, -5.96, 7.03, -0.11, -1.86, 1.77, -2.49, 1.64, -3.05, -5.24],
            [-8.59, 8.41, 3.76, 3.77, 5.69, 1.75, -3.2, -4.0, -4.0, 6.85],
            4,
            inf,
            "e",
            -0.3055952380,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [7.95, -5.96, 7.03, -0.11, -1.86, 1.77, -2.49, 1.64, -3.05, -5.24],
            [11.08, 8.41, 11.47, 8.78, 14.09, 6.03, 10.67, 9.45, 12.72, 11.12],
            4,
            inf,
            "e",
            -0.29257936507,
        ),
        (
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            [7.95, -5.96, 7.03, -0.11, -1.86, 1.77, -2.49, 1.64, -3.05, -5.24],
            [-2.49, 1.64, -3.05, 7.95, -5.96, 1.77, -5.24, 7.03, -0.11, -1.86],
            4,
            inf,
            "e",
            -0.27,
        ),
        (
            [0.32, -0.89, -0.01, 1.56, 0.24, 1.78, -1.63, 0.82, 0.12, 2.29],
            [0.22, -0.99, -0.11, 1.46, 0.14, 1.68, -1.73, 0.72, 0.02, 2.19],
            [0.20, -0.97, 0.11, 1.16, 0.14, 1.18, -1.43, 0.72, 0.02, 2.29],
            4,
            inf,
            "e",
            -0.0914285714,
        ),
        (
            [1.8, 1.1, 1.8, 1.1, 1.8, -2.0, 1.1, 1.8, -2.0, 1.1],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            4,
            inf,
            "e",
            -0.45,
        ),
        (
            [1.8, 1.1, 1.8, 1.1, 1.8, -2.0, 1.1, 1.8, -2.0, 1.1],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            [-0.6, 0.4, -0.6, -0.6, -1.3, -1.3, -1.3, -0.6, -0.6, 0.4],
            4,
            inf,
            2,
            -0.6492127,
        ),
        (
            [1.04, 1.23, 0.92, 1.1, 1.34],
            [1.3, 1.1, 0.9, 1.2, 1.0],
            [1.0, 0.9, 1.2, 1.3, 1.1],
            3,
            inf,
            10,
            -0.14476482,
        ),
    ],
)
def test_ksg_cmi(data_x, data_y, cond, k, minkowski_p, base, expected):
    """Test the conditional
    Kraskov-Stoegbauer-Grassberger mutual information estimator."""
    est = KSGCMIEstimator(
        data_x,
        data_y,
        cond=cond,
        k=k,
        minkowski_p=minkowski_p,
        noise_level=0,  # for reproducibility
        base=base,
    )
    assert isinstance(est.result(), float)
    assert est.result() == pytest.approx(expected)
    assert isinstance(est.local_vals(), ndarray)


@pytest.mark.parametrize(
    "rng_int,method,p_mi,p_cmi",
    [
        (1, "permutation_test", 0.42, 0.2),
        (1, "bootstrap", 0.38, 0.1),
        (2, "permutation_test", 0.1, 0.12),
        (2, "bootstrap", 0.1, 0.12),
        (3, "permutation_test", 0.54, 0.12),
        (3, "bootstrap", 0.48, 0.04),
        (4, "permutation_test", 0.04, 0.26),
        (4, "bootstrap", 0.06, 0.16),
    ],
)
def test_ksg_mi_statistical_test(rng_int, method, p_mi, p_cmi):
    """Test the KSG MI for p-values. Fix rng."""
    data_x, data_y, cond = generate_autoregressive_series_condition(
        rng_int, alpha=(0.5, 0.1), beta=0.6, gamma=(0.4, 0.2)
    )
    est_mi = KSGMIEstimator(
        data_x, data_y, k=4, minkowski_p=inf, noise_level=0, base=2, seed=8
    )
    est_cmi = KSGCMIEstimator(
        data_x, data_y, cond=cond, k=4, minkowski_p=inf, noise_level=0, base=2, seed=8
    )
    test = est_mi.statistical_test(method=method, n_tests=50)
    assert test.p_value == pytest.approx(p_mi)
    test = est_cmi.statistical_test(method=method, n_tests=50)
    assert test.p_value == pytest.approx(p_cmi)
