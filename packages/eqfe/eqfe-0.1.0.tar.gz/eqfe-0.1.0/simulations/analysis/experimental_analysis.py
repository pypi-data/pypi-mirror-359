"""
Experimental Data Analysis Module

This module provides comprehensive tools for analyzing experimental data
from environmental quantum field effect measurements, including CHSH tests,
field correlations, and statistical validation.
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize, signal
from scipy.special import erfc
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
import warnings

from .physics_validator import QuantumBoundsValidator, ValidationResult


@dataclass
class ExperimentalData:
    """Container for experimental measurement data."""

    timestamps: np.ndarray
    chsh_values: np.ndarray
    correlations: Dict[str, np.ndarray]
    environmental_fields: Dict[str, np.ndarray]
    detector_counts: Dict[str, np.ndarray]
    analyzer_settings: Dict[str, np.ndarray]
    metadata: Dict = field(default_factory=dict)


@dataclass
class AnalysisResults:
    """Container for analysis results."""

    amplification_params: Dict[str, float]
    correlation_coefficients: Dict[str, float]
    statistical_tests: Dict[str, Dict]
    fit_quality: Dict[str, float]
    validation_results: ValidationResult
    plots: Dict[str, str] = field(default_factory=dict)


class CHSHAnalyzer:
    """
    Analyzer for CHSH Bell test experimental data with environmental correlations.
    """

    def __init__(self, validator: Optional[QuantumBoundsValidator] = None):
        """
        Initialize CHSH analyzer.

        Parameters:
        -----------
        validator : QuantumBoundsValidator, optional
            Physics bounds validator
        """
        self.validator = validator or QuantumBoundsValidator()
        self.tsirelson_bound = 2 * np.sqrt(2)
        self.classical_bound = 2.0

    def calculate_chsh_parameter(
        self, correlations: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Calculate CHSH parameter from correlation measurements.

        Parameters:
        -----------
        correlations : dict
            Dictionary with keys 'E_00', 'E_01', 'E_10', 'E_11' for
            correlations E(a,b) where a,b are analyzer settings

        Returns:
        --------
        array : CHSH parameter values S
        """
        try:
            E_00 = correlations["E_00"]  # Alice 0°, Bob 22.5°
            E_01 = correlations["E_01"]  # Alice 0°, Bob 67.5°
            E_10 = correlations["E_10"]  # Alice 45°, Bob 22.5°
            E_11 = correlations["E_11"]  # Alice 45°, Bob 67.5°

            # CHSH inequality: S = |E(a₀,b₀) - E(a₀,b₁)| + |E(a₁,b₀) + E(a₁,b₁)|
            S = np.abs(E_00 - E_01) + np.abs(E_10 + E_11)

            return S

        except KeyError as e:
            raise ValueError(f"Missing correlation measurement: {e}")

    def correlation_from_counts(
        self, counts: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Calculate correlation functions from raw detection counts.

        Parameters:
        -----------
        counts : dict
            Detection counts with keys like 'AB_00', 'AB_01', etc.
            for coincidence counts between detectors A and B

        Returns:
        --------
        dict : Correlation functions E(a,b)
        """
        correlations = {}

        # Standard CHSH analyzer settings
        settings = ["00", "01", "10", "11"]

        for setting in settings:
            try:
                # Coincidence counts for all four combinations (++, +-, -+, --)
                N_pp = counts[f"AB_{setting}_pp"]  # Both detectors fire
                N_pm = counts[f"AB_{setting}_pm"]  # A fires, B doesn't
                N_mp = counts[f"AB_{setting}_mp"]  # A doesn't fire, B fires
                N_mm = counts[f"AB_{setting}_mm"]  # Neither fires

                # Calculate correlation: E = (N++ + N-- - N+- - N-+) / (N++ + N-- + N+- + N-+)
                numerator = N_pp + N_mm - N_pm - N_mp
                denominator = N_pp + N_mm + N_pm + N_mp

                # Avoid division by zero
                mask = denominator > 0
                E = np.zeros_like(numerator, dtype=float)
                E[mask] = numerator[mask] / denominator[mask]

                correlations[f"E_{setting}"] = E

            except KeyError:
                warnings.warn(f"Missing count data for setting {setting}")

        return correlations

    def analyze_time_evolution(self, data: ExperimentalData) -> Dict:
        """
        Analyze time evolution of CHSH parameters.

        Parameters:
        -----------
        data : ExperimentalData
            Experimental data including timestamps and CHSH values

        Returns:
        --------
        dict : Time evolution analysis results
        """
        results = {}

        # Sort by timestamp
        sort_idx = np.argsort(data.timestamps)
        times = data.timestamps[sort_idx]
        chsh = data.chsh_values[sort_idx]

        # Calculate running average
        window_size = min(100, len(chsh) // 10)
        chsh_smooth = signal.savgol_filter(chsh, window_size, 3)

        # Find maximum and time to maximum
        max_idx = np.argmax(chsh_smooth)
        max_time = times[max_idx]
        max_chsh = chsh_smooth[max_idx]

        # Calculate time derivatives
        dt = np.diff(times)
        dS_dt = np.diff(chsh_smooth) / dt

        # Initial slope (enhancement rate)
        initial_mask = times[1:] < times[0] + (times[-1] - times[0]) * 0.1
        if np.any(initial_mask):
            initial_slope = np.mean(dS_dt[initial_mask])
        else:
            initial_slope = dS_dt[0]

        results.update(
            {
                "max_chsh": max_chsh,
                "time_to_max": max_time,
                "initial_enhancement_rate": initial_slope,
                "times": times,
                "chsh_smooth": chsh_smooth,
                "enhancement_phase_duration": max_time,
            }
        )

        return results

    def fit_amplification_law(
        self,
        times: np.ndarray,
        chsh_values: np.ndarray,
        field_variance: np.ndarray,
    ) -> Dict:
        """
        Fit the theoretical amplification law to experimental data.

        Parameters:
        -----------
        times : array
            Measurement timestamps
        chsh_values : array
            Measured CHSH parameter values
        field_variance : array
            Environmental field variance ⟨φ²⟩

        Returns:
        --------
        dict : Fit parameters and quality metrics
        """
        # Amplification law: S(t) = S₀ * exp[α⟨φ²⟩t - β∫C(τ)dτ]
        # For short times: S(t) ≈ S₀ * (1 + α⟨φ²⟩t - βt/τ_c)

        def amplification_model(t, S0, alpha, beta, tau_c):
            """Simplified amplification law model."""
            integral_term = np.where(
                t < tau_c, t**2 / (2 * tau_c), t - tau_c / 2
            )
            return S0 * np.exp(
                alpha * np.mean(field_variance) * t - beta * integral_term
            )

        # Initial parameter guesses
        S0_guess = np.mean(chsh_values[:10])  # Initial CHSH value
        alpha_guess = 0.001  # Small enhancement
        beta_guess = 0.0001  # Small decoherence
        tau_c_guess = np.max(times) / 10  # Correlation time estimate

        initial_guess = [S0_guess, alpha_guess, beta_guess, tau_c_guess]

        try:
            # Perform fit
            popt, pcov = optimize.curve_fit(
                amplification_model,
                times,
                chsh_values,
                p0=initial_guess,
                bounds=([1.0, 0, 0, 0], [4.0, 1.0, 1.0, np.max(times)]),
                maxfev=5000,
            )

            S0_fit, alpha_fit, beta_fit, tau_c_fit = popt

            # Calculate fit quality
            fitted_values = amplification_model(times, *popt)
            r_squared = 1 - np.sum(
                (chsh_values - fitted_values) ** 2
            ) / np.sum((chsh_values - np.mean(chsh_values)) ** 2)
            chi_squared = np.sum(
                (chsh_values - fitted_values) ** 2 / fitted_values
            )
            reduced_chi_squared = chi_squared / (len(times) - len(popt))

            # Parameter uncertainties
            param_errors = np.sqrt(np.diag(pcov))

            fit_results = {
                "S0": S0_fit,
                "alpha": alpha_fit,
                "beta": beta_fit,
                "tau_c": tau_c_fit,
                "S0_error": param_errors[0],
                "alpha_error": param_errors[1],
                "beta_error": param_errors[2],
                "tau_c_error": param_errors[3],
                "r_squared": r_squared,
                "chi_squared": chi_squared,
                "reduced_chi_squared": reduced_chi_squared,
                "fitted_values": fitted_values,
                "fit_success": True,
            }

        except (RuntimeError, ValueError) as e:
            warnings.warn(f"Amplification law fit failed: {e}")
            fit_results = {"fit_success": False, "error_message": str(e)}

        return fit_results


class EnvironmentalCorrelationAnalyzer:
    """
    Analyzer for correlations between quantum measurements and environmental fields.
    """

    def __init__(self):
        self.correlation_methods = ["pearson", "spearman", "kendall"]

    def calculate_field_variance(
        self, field_data: np.ndarray, window_size: int = 100
    ) -> np.ndarray:
        """
        Calculate running variance of environmental field.

        Parameters:
        -----------
        field_data : array
            Environmental field measurements
        window_size : int
            Window size for running variance calculation

        Returns:
        --------
        array : Field variance ⟨φ²⟩
        """
        # Calculate running variance using pandas for efficiency
        field_series = pd.Series(field_data)
        rolling_var = field_series.rolling(
            window=window_size, center=True
        ).var()

        # Fill NaN values at edges
        rolling_var = rolling_var.bfill().ffill()

        return rolling_var.values

    def correlation_analysis(
        self,
        chsh_values: np.ndarray,
        field_variance: np.ndarray,
        method: str = "pearson",
    ) -> Dict:
        """
        Analyze correlation between CHSH parameter and field variance.

        Parameters:
        -----------
        chsh_values : array
            CHSH parameter measurements
        field_variance : array
            Environmental field variance
        method : str
            Correlation method ('pearson', 'spearman', 'kendall')

        Returns:
        --------
        dict : Correlation analysis results
        """
        if method == "pearson":
            corr_coef, p_value = stats.pearsonr(chsh_values, field_variance)
        elif method == "spearman":
            corr_coef, p_value = stats.spearmanr(chsh_values, field_variance)
        elif method == "kendall":
            corr_coef, p_value = stats.kendalltau(chsh_values, field_variance)
        else:
            raise ValueError(f"Unknown correlation method: {method}")

        # Effect size classification (Cohen's conventions)
        if abs(corr_coef) < 0.1:
            effect_size = "negligible"
        elif abs(corr_coef) < 0.3:
            effect_size = "small"
        elif abs(corr_coef) < 0.5:
            effect_size = "medium"
        else:
            effect_size = "large"

        # Statistical significance
        alpha = 0.001  # Significance level
        is_significant = p_value < alpha

        return {
            "correlation_coefficient": corr_coef,
            "p_value": p_value,
            "is_significant": is_significant,
            "effect_size": effect_size,
            "method": method,
            "n_samples": len(chsh_values),
        }

    def lag_correlation_analysis(
        self,
        chsh_values: np.ndarray,
        field_variance: np.ndarray,
        max_lag: int = 100,
    ) -> Dict:
        """
        Analyze time-lagged correlations between CHSH and field variance.

        Parameters:
        -----------
        chsh_values : array
            CHSH parameter measurements
        field_variance : array
            Environmental field variance
        max_lag : int
            Maximum lag to consider

        Returns:
        --------
        dict : Lag correlation analysis results
        """
        lags = np.arange(-max_lag, max_lag + 1)
        correlations = []

        for lag in lags:
            if lag == 0:
                corr = stats.pearsonr(chsh_values, field_variance)[0]
            elif lag > 0:
                # Field leads CHSH
                corr = stats.pearsonr(
                    chsh_values[lag:], field_variance[:-lag]
                )[0]
            else:
                # CHSH leads field
                corr = stats.pearsonr(
                    chsh_values[:lag], field_variance[-lag:]
                )[0]

            correlations.append(corr)

        correlations = np.array(correlations)

        # Find optimal lag
        max_corr_idx = np.argmax(np.abs(correlations))
        optimal_lag = lags[max_corr_idx]
        max_correlation = correlations[max_corr_idx]

        return {
            "lags": lags,
            "correlations": correlations,
            "optimal_lag": optimal_lag,
            "max_correlation": max_correlation,
        }


class StatisticalValidator:
    """
    Statistical validation and hypothesis testing for experimental results.
    """

    def __init__(self, alpha: float = 0.001):
        """
        Initialize statistical validator.

        Parameters:
        -----------
        alpha : float
            Significance level for hypothesis tests
        """
        self.alpha = alpha

    def bell_inequality_test(self, chsh_values: np.ndarray) -> Dict:
        """
        Test for violations of Bell inequality and Tsirelson bound.

        Parameters:
        -----------
        chsh_values : array
            CHSH parameter measurements

        Returns:
        --------
        dict : Statistical test results
        """
        tsirelson_bound = 2 * np.sqrt(2)
        classical_bound = 2.0

        # Test against classical bound (S > 2)
        classical_violations = np.sum(chsh_values > classical_bound)
        classical_fraction = classical_violations / len(chsh_values)

        # One-sided t-test against classical bound
        t_stat_classical, p_value_classical = stats.ttest_1samp(
            chsh_values, classical_bound, alternative="greater"
        )

        # Test against Tsirelson bound (S > 2√2)
        tsirelson_violations = np.sum(chsh_values > tsirelson_bound)
        tsirelson_fraction = tsirelson_violations / len(chsh_values)

        # One-sided t-test against Tsirelson bound
        t_stat_tsirelson, p_value_tsirelson = stats.ttest_1samp(
            chsh_values, tsirelson_bound, alternative="greater"
        )

        # Effect sizes (Cohen's d)
        mean_chsh = np.mean(chsh_values)
        std_chsh = np.std(chsh_values)

        cohen_d_classical = (mean_chsh - classical_bound) / std_chsh
        cohen_d_tsirelson = (mean_chsh - tsirelson_bound) / std_chsh

        return {
            "classical_violations": classical_violations,
            "classical_fraction": classical_fraction,
            "classical_p_value": p_value_classical,
            "classical_significant": p_value_classical < self.alpha,
            "cohen_d_classical": cohen_d_classical,
            "tsirelson_violations": tsirelson_violations,
            "tsirelson_fraction": tsirelson_fraction,
            "tsirelson_p_value": p_value_tsirelson,
            "tsirelson_significant": p_value_tsirelson < self.alpha,
            "cohen_d_tsirelson": cohen_d_tsirelson,
            "mean_chsh": mean_chsh,
            "std_chsh": std_chsh,
        }

    def environmental_correlation_test(
        self, correlation_coef: float, n_samples: int
    ) -> Dict:
        """
        Test significance of environmental correlation.

        Parameters:
        -----------
        correlation_coef : float
            Correlation coefficient
        n_samples : int
            Number of samples

        Returns:
        --------
        dict : Correlation test results
        """
        # Fisher z-transformation for significance testing
        z_score = 0.5 * np.log((1 + correlation_coef) / (1 - correlation_coef))
        standard_error = 1 / np.sqrt(n_samples - 3)

        # Two-sided test against null hypothesis (ρ = 0)
        z_stat = z_score / standard_error
        p_value = 2 * (1 - stats.norm.cdf(np.abs(z_stat)))

        # Confidence interval for correlation
        z_critical = stats.norm.ppf(1 - self.alpha / 2)
        z_lower = z_score - z_critical * standard_error
        z_upper = z_score + z_critical * standard_error

        # Transform back to correlation scale
        corr_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        corr_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)

        return {
            "correlation": correlation_coef,
            "z_score": z_score,
            "p_value": p_value,
            "is_significant": p_value < self.alpha,
            "confidence_interval": (corr_lower, corr_upper),
            "n_samples": n_samples,
        }

    def power_analysis(
        self,
        effect_size: float,
        n_samples: int,
        test_type: str = "correlation",
    ) -> Dict:
        """
        Calculate statistical power for given effect size and sample size.

        Parameters:
        -----------
        effect_size : float
            Expected effect size (correlation coefficient or Cohen's d)
        n_samples : int
            Sample size
        test_type : str
            Type of test ('correlation' or 't_test')

        Returns:
        --------
        dict : Power analysis results
        """
        if test_type == "correlation":
            # Power for correlation test
            z_alpha = stats.norm.ppf(1 - self.alpha / 2)
            z_beta = (
                0.5
                * np.log((1 + effect_size) / (1 - effect_size))
                * np.sqrt(n_samples - 3)
            )
            power = (
                1
                - stats.norm.cdf(z_alpha - z_beta)
                + stats.norm.cdf(-z_alpha - z_beta)
            )

        elif test_type == "t_test":
            # Power for one-sample t-test
            from scipy.stats import nct

            df = n_samples - 1
            nc = effect_size * np.sqrt(n_samples)
            t_critical = stats.t.ppf(1 - self.alpha, df)
            power = 1 - nct.cdf(t_critical, df, nc)

        else:
            raise ValueError(f"Unknown test type: {test_type}")

        return {
            "power": power,
            "effect_size": effect_size,
            "n_samples": n_samples,
            "alpha": self.alpha,
            "test_type": test_type,
        }


def comprehensive_analysis(data: ExperimentalData) -> AnalysisResults:
    """
    Perform comprehensive analysis of experimental data.

    Parameters:
    -----------
    data : ExperimentalData
        Complete experimental dataset

    Returns:
    --------
    AnalysisResults : Complete analysis results
    """
    # Initialize analyzers
    chsh_analyzer = CHSHAnalyzer()
    env_analyzer = EnvironmentalCorrelationAnalyzer()
    stat_validator = StatisticalValidator()

    # Physics validation
    validation_result = chsh_analyzer.validator.comprehensive_validation(
        S=data.chsh_values
    )

    # Time evolution analysis
    time_results = chsh_analyzer.analyze_time_evolution(data)

    # Environmental correlation
    field_variance = env_analyzer.calculate_field_variance(
        data.environmental_fields.get(
            "magnetic_field", np.zeros_like(data.timestamps)
        )
    )

    correlation_results = env_analyzer.correlation_analysis(
        data.chsh_values, field_variance
    )

    # Amplification law fitting
    fit_results = chsh_analyzer.fit_amplification_law(
        data.timestamps, data.chsh_values, field_variance
    )

    # Statistical tests
    bell_test_results = stat_validator.bell_inequality_test(data.chsh_values)

    # Compile results
    results = AnalysisResults(
        amplification_params=fit_results,
        correlation_coefficients={
            "field_correlation": correlation_results["correlation_coefficient"]
        },
        statistical_tests={
            "bell_test": bell_test_results,
            "correlation_test": correlation_results,
        },
        fit_quality={"r_squared": fit_results.get("r_squared", 0)},
        validation_results=validation_result,
    )

    return results


if __name__ == "__main__":
    # Example usage and testing
    print("Experimental Data Analysis Module")
    print("=" * 50)

    # Generate synthetic test data
    np.random.seed(42)
    n_points = 1000

    # Synthetic timestamps
    timestamps = np.linspace(0, 100, n_points)

    # Synthetic environmental field with correlations
    field_correlation_time = 10.0
    field_data = np.random.normal(0, 1, n_points)
    # Add some temporal correlation
    for i in range(1, n_points):
        field_data[i] += (
            0.3 * field_data[i - 1] * np.exp(-1 / field_correlation_time)
        )

    # Synthetic CHSH data with environmental correlation
    base_chsh = 2.4
    enhancement = 0.1 * np.abs(field_data)
    chsh_values = base_chsh + enhancement + np.random.normal(0, 0.05, n_points)

    # Create test data structure
    test_data = ExperimentalData(
        timestamps=timestamps,
        chsh_values=chsh_values,
        correlations={},
        environmental_fields={"magnetic_field": field_data},
        detector_counts={},
        analyzer_settings={},
    )

    # Run comprehensive analysis
    results = comprehensive_analysis(test_data)

    print(f"Analysis complete!")
    print(
        f"Physics validation: {'PASSED' if results.validation_results.is_valid else 'FAILED'}"
    )
    print(
        f"Field correlation: {results.correlation_coefficients['field_correlation']:.4f}"
    )
    print(f"Fit quality (R²): {results.fit_quality['r_squared']:.4f}")

    if results.statistical_tests["bell_test"]["classical_significant"]:
        print("✓ Significant violation of classical Bell inequality")
    else:
        print("✗ No significant violation of classical Bell inequality")

    if results.statistical_tests["correlation_test"]["is_significant"]:
        print("✓ Significant environmental correlation detected")
    else:
        print("✗ No significant environmental correlation detected")
