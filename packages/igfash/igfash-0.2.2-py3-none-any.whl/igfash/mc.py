# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:11:30 2025

@author: ftong
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)

# from Mizrahi et al., 2021
def empirical_cdf(sample, weights=None):
    try:
        sample = sample.values
    except BaseException:
        pass
    try:
        weights = weights.values
    except BaseException:
        pass

    sample_idxs_sorted = np.argsort(sample)
    sample_sorted = sample[sample_idxs_sorted]
    if weights is not None:
        weights_sorted = weights[sample_idxs_sorted]
        x, y = sample_sorted, np.cumsum(weights_sorted) / weights_sorted.sum()
    else:
        x, y = sample_sorted, np.arange(1, len(sample) + 1) / len(sample)

    # only return one value per bin
    x, y_count = np.unique(x, return_counts=True)
    return x, y[np.cumsum(y_count) - 1]

def fitted_cdf_discrete(sample, mc, delta_m, x_max=None, beta=None):
    if beta is None:
        beta = estimate_beta_tinti(sample, mc=mc, delta_m=delta_m)

    if x_max is None:
        sample_bin_n = (sample.max() - mc) / delta_m
    else:
        sample_bin_n = (x_max - mc) / delta_m
    bins = np.arange(sample_bin_n + 1)
    cdf = 1 - np.exp(-beta * delta_m * (bins + 1))
    x, y = mc + bins * delta_m, cdf

    x, y_count = np.unique(x, return_counts=True)
    return x, y[np.cumsum(y_count) - 1]

def simulate_magnitudes(n, beta, mc, m_max=None):
    if m_max is not None:
        norm_factor = (1 - np.exp(-beta * (m_max - mc)))
    else:
        norm_factor = 1
    mags = np.random.uniform(size=n)
    mags = (-1 * np.log(1 - norm_factor * mags) / beta) + mc
    return mags


def round_half_up(n, decimals=0):
    # this is because numpy does weird rounding.
    multiplier = 10 ** decimals
    return np.floor(n * multiplier + 0.5) / multiplier

def estimate_beta_tinti(magnitudes, mc, weights=None, axis=None, delta_m=0):
    """
    Tinti, S., & Mulargia, F. (1987). Confidence intervals of b values
    for grouped magnitudes. Bulletin of the Seismological Society of
    America, 77(6), 2125-2134.
    """

    if delta_m > 0:
        p = (1 + (delta_m / (np.average(
            magnitudes - mc, weights=weights, axis=axis))))
        beta = 1 / delta_m * np.log(p)
    else:
        beta = 1 / np.average((magnitudes - (mc - delta_m / 2)),
                              weights=weights, axis=axis)
    return beta

def ks_test_gr(sample, mc, delta_m, ks_ds=None, n_samples=10000, beta=None):
    sample = sample[sample >= mc - delta_m / 2]
    if len(sample) == 0:
        logger.debug("no sample")
        return 1, 0, []
    if len(np.unique(sample)) == 1:
        logger.debug("sample contains only one value")
        return 1, 0, []
    if beta is None:
        beta = estimate_beta_tinti(sample, mc=mc, delta_m=delta_m)

    if ks_ds is None:
        ks_ds = []

        n_sample = len(sample)
        simulated_all = round_half_up(
            simulate_magnitudes(
                mc=mc - delta_m / 2,
                beta=beta,
                n=n_samples * n_sample) / delta_m) * delta_m

        x_max = np.max(simulated_all)
        x_fit, y_fit = fitted_cdf_discrete(
            sample, mc=mc, delta_m=delta_m, x_max=x_max, beta=beta)

        for i in range(n_samples):
            simulated = simulated_all[n_sample * i:n_sample * (i + 1)].copy()
            x_emp, y_emp = empirical_cdf(simulated)
            y_fit_int = np.interp(x_emp, x_fit, y_fit)

            ks_d = np.max(np.abs(y_emp - y_fit_int))
            ks_ds.append(ks_d)
    else:
        x_fit, y_fit = fitted_cdf_discrete(
            sample, mc=mc, delta_m=delta_m, beta=beta)

    x_emp, y_emp = empirical_cdf(sample)
    y_emp_int = np.interp(x_fit, x_emp, y_emp)

    orig_ks_d = np.max(np.abs(y_fit - y_emp_int))

    return orig_ks_d, sum(ks_ds >= orig_ks_d) / len(ks_ds), ks_ds

def estimate_mc(sample,
                mcs_test,
                delta_m,
                p_pass,
                stop_when_passed=True,
                beta=None,
                n_samples=10000):
    """
    Estimates mc.

    Parameters
    ----------
    sample : np.array
        Magnitudes to test.
    mcs_test : np.array
        Completeness magnitudes to test.
    delta_m : float
        Magnitude bins (sample has to be rounded to bins beforehand).
    p_pass : float
        P-value with which the test is passed.
    stop_when_passed : bool
        Stop calculations when first mc passes the test.
    beta : float
        If beta is 'known', only estimate mc.
    n_samples : int
        Number of magnitude samples to be generated in p-value
        calculation of KS distance.
    """

    ks_ds = []
    ps = []
    i = 0
    for mc in mcs_test:
        logger.debug(f"testing mc {mc}")
        ks_d, p, _ = ks_test_gr(
            sample, mc=mc, delta_m=delta_m, n_samples=n_samples, beta=beta)

        ks_ds.append(ks_d)
        ps.append(p)

        i += 1
        logger.debug(f"..p-value: {p}")

        if p >= p_pass and stop_when_passed:
            break
    ps = np.array(ps)
    if np.any(ps >= p_pass):
        best_mc = mcs_test[np.argmax(ps >= p_pass)]
        if beta is None:
            beta = estimate_beta_tinti(
                sample[sample >= best_mc - delta_m / 2],
                mc=best_mc, delta_m=delta_m)
        logger.debug(f"First mc to pass the test: {best_mc} with a beta of: {beta}")
    else:
        best_mc = None
        beta = None
        logger.debug("None of the mcs passed the test.")
    return mcs_test, ks_ds, ps, best_mc, beta