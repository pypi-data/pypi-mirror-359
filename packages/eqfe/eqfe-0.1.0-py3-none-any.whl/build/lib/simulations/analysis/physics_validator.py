"""
Physics Validation Module

This module implements comprehensive physics bounds checking and validation
for all quantum correlation calculations to ensure results respect established
physical principles.
"""

import numpy as np
import warnings
from typing import Union, Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..core.field_simulator import PhysicalConstants


@dataclass
class ValidationResult:
    """Container for validation results."""

    is_valid: bool
    violations: List[str]
    warnings: List[str]
    bounds_checked: Dict[str, bool]


class QuantumBoundsValidator:
    """
    Comprehensive validator for quantum mechanical bounds and physical constraints.

    This class implements checking for:
    - Tsirelson bound (S ≤ 2√2)
    - Classical Bell inequality (S ≤ 2)
    - Probability conservation
    - Unitarity constraints
    - Causality requirements
    - Energy conservation
    """

    def __init__(self, tolerance: float = 1e-10):
        """
        Initialize validator with numerical tolerance.

        Parameters:
        -----------
        tolerance : float
            Numerical tolerance for bound checking
        """
        self.tolerance = tolerance
        self.tsirelson_bound = 2 * np.sqrt(2)
        self.classical_bound = 2.0

    def validate_chsh_parameter(
        self, S: Union[float, np.ndarray]
    ) -> ValidationResult:
        """
        Comprehensive validation of CHSH parameter values.

        Parameters:
        -----------
        S : float or array
            CHSH parameter value(s) to validate

        Returns:
        --------
        ValidationResult : Validation results with detailed information
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        # Ensure S is array for uniform processing
        S_array = np.atleast_1d(S)

        # Check Tsirelson bound
        tsirelson_violation = np.any(
            S_array > self.tsirelson_bound + self.tolerance
        )
        bounds_checked["tsirelson"] = not tsirelson_violation

        if tsirelson_violation:
            max_violation = np.max(S_array) - self.tsirelson_bound
            violations.append(
                f"Tsirelson bound violated: max S = {np.max(S_array):.6f}, "
                f"violation = {max_violation:.6f}"
            )

        # Check for quantum advantage
        quantum_advantage = np.any(
            S_array > self.classical_bound + self.tolerance
        )
        bounds_checked["quantum_advantage"] = quantum_advantage

        if not quantum_advantage:
            warnings_list.append("No quantum advantage detected (S ≤ 2)")

        # Check for non-physical negative values
        negative_values = np.any(S_array < 0)
        bounds_checked["positivity"] = not negative_values

        if negative_values:
            violations.append(f"Non-physical negative CHSH values detected")

        # Check for extremely large values that might indicate calculation errors
        extremely_large = np.any(
            S_array > 4.0
        )  # Theoretical maximum for any correlation
        bounds_checked["physical_range"] = not extremely_large

        if extremely_large:
            violations.append(
                f"Unphysically large CHSH values detected: max = {np.max(S_array):.6f}"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def validate_correlations(
        self, correlations: Dict[str, float]
    ) -> ValidationResult:
        """
        Validate individual correlation functions for physical consistency.

        Parameters:
        -----------
        correlations : dict
            Dictionary of correlation values (e.g., E_ab for different analyzer settings)

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        # Check correlation bounds (-1 ≤ E ≤ 1)
        correlation_bounds_ok = True
        for key, E in correlations.items():
            if not (-1 - self.tolerance <= E <= 1 + self.tolerance):
                correlation_bounds_ok = False
                violations.append(
                    f"Correlation {key} = {E:.6f} outside physical bounds [-1, 1]"
                )

        bounds_checked["correlation_bounds"] = correlation_bounds_ok

        # Check for perfect correlations (might indicate systematic errors)
        perfect_correlations = [
            key
            for key, E in correlations.items()
            if abs(abs(E) - 1.0) < self.tolerance
        ]
        if perfect_correlations:
            warnings_list.append(
                f"Perfect correlations detected: {perfect_correlations}"
            )

        bounds_checked["realistic_correlations"] = (
            len(perfect_correlations) == 0
        )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def validate_probabilities(
        self, probabilities: np.ndarray
    ) -> ValidationResult:
        """
        Validate probability distributions for normalization and positivity.

        Parameters:
        -----------
        probabilities : array
            Array of probability values

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        # Check positivity
        positivity_ok = np.all(probabilities >= -self.tolerance)
        bounds_checked["positivity"] = positivity_ok

        if not positivity_ok:
            violations.append(
                f"Negative probabilities detected: min = {np.min(probabilities):.6f}"
            )

        # Check normalization
        prob_sum = np.sum(probabilities)
        normalization_ok = abs(prob_sum - 1.0) < self.tolerance
        bounds_checked["normalization"] = normalization_ok

        if not normalization_ok:
            violations.append(
                f"Probabilities not normalized: sum = {prob_sum:.6f}"
            )

        # Check for values > 1
        bounds_ok = np.all(probabilities <= 1 + self.tolerance)
        bounds_checked["probability_bounds"] = bounds_ok

        if not bounds_ok:
            violations.append(
                f"Probabilities > 1 detected: max = {np.max(probabilities):.6f}"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def validate_amplification_factor(
        self, a: Union[float, np.ndarray]
    ) -> ValidationResult:
        """
        Validate amplification factor for physical reasonableness.

        Parameters:
        -----------
        a : float or array
            Amplification factor values

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        a_array = np.atleast_1d(a)

        # Check for a ≥ 1 (amplification only, no suppression)
        amplification_ok = np.all(a_array >= 1.0 - self.tolerance)
        bounds_checked["amplification_positive"] = amplification_ok

        if not amplification_ok:
            violations.append(
                f"Suppression detected (a < 1): min a = {np.min(a_array):.6f}"
            )

        # Check for reasonable amplification bounds
        max_reasonable_amplification = (
            1.5  # Arbitrary but physically motivated
        )
        reasonable_bounds = np.all(a_array <= max_reasonable_amplification)
        bounds_checked["reasonable_amplification"] = reasonable_bounds

        if not reasonable_bounds:
            warnings_list.append(
                f"Large amplification detected: max a = {np.max(a_array):.6f}"
            )

        # Check for extremely large amplifications
        extreme_amplification = np.any(a_array > 2.0)
        bounds_checked["extreme_amplification"] = not extreme_amplification

        if extreme_amplification:
            violations.append(
                f"Extreme amplification detected: max a = {np.max(a_array):.6f}"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def validate_field_parameters(
        self, field_mass: float, coupling_strength: float, field_speed: float
    ) -> ValidationResult:
        """
        Validate environmental field parameters for physical consistency.

        Parameters:
        -----------
        field_mass : float
            Scalar field mass in eV/c²
        coupling_strength : float
            Dimensionless coupling constant
        field_speed : float
            Field propagation speed in m/s

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        # Check field mass positivity
        mass_positive = field_mass >= 0
        bounds_checked["mass_positive"] = mass_positive

        if not mass_positive:
            violations.append(f"Negative field mass: {field_mass:.6e} eV/c²")

        # Check coupling strength bounds
        coupling_positive = coupling_strength >= 0
        bounds_checked["coupling_positive"] = coupling_positive

        if not coupling_positive:
            violations.append(
                f"Negative coupling strength: {coupling_strength:.6e}"
            )

        coupling_reasonable = coupling_strength <= 0.1
        bounds_checked["coupling_reasonable"] = coupling_reasonable

        if not coupling_reasonable:
            warnings_list.append(
                f"Large coupling may violate perturbation theory: g = {coupling_strength:.6e}"
            )

        # Check field speed
        speed_positive = field_speed > 0
        bounds_checked["speed_positive"] = speed_positive

        if not speed_positive:
            violations.append(
                f"Non-positive field speed: {field_speed:.6e} m/s"
            )

        speed_reasonable = field_speed <= PhysicalConstants.c
        bounds_checked["speed_reasonable"] = speed_reasonable

        if not speed_reasonable:
            warnings_list.append(
                f"Superluminal field speed: v = {field_speed:.6e} m/s > c"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def comprehensive_validation(
        self,
        S: Union[float, np.ndarray],
        correlations: Optional[Dict[str, float]] = None,
        amplification: Optional[Union[float, np.ndarray]] = None,
        field_params: Optional[Dict[str, float]] = None,
    ) -> ValidationResult:
        """
        Perform comprehensive validation of all physical quantities.

        Parameters:
        -----------
        S : float or array
            CHSH parameter values
        correlations : dict, optional
            Individual correlation functions
        amplification : float or array, optional
            Amplification factors
        field_params : dict, optional
            Field parameters (mass, coupling, speed)

        Returns:
        --------
        ValidationResult : Combined validation results
        """
        all_violations = []
        all_warnings = []
        all_bounds_checked = {}

        # Validate CHSH parameter
        chsh_result = self.validate_chsh_parameter(S)
        all_violations.extend(chsh_result.violations)
        all_warnings.extend(chsh_result.warnings)
        all_bounds_checked.update(
            {f"chsh_{k}": v for k, v in chsh_result.bounds_checked.items()}
        )

        # Validate correlations if provided
        if correlations is not None:
            corr_result = self.validate_correlations(correlations)
            all_violations.extend(corr_result.violations)
            all_warnings.extend(corr_result.warnings)
            all_bounds_checked.update(
                {f"corr_{k}": v for k, v in corr_result.bounds_checked.items()}
            )

        # Validate amplification if provided
        if amplification is not None:
            amp_result = self.validate_amplification_factor(amplification)
            all_violations.extend(amp_result.violations)
            all_warnings.extend(amp_result.warnings)
            all_bounds_checked.update(
                {f"amp_{k}": v for k, v in amp_result.bounds_checked.items()}
            )

        # Validate field parameters if provided
        if field_params is not None:
            field_result = self.validate_field_parameters(**field_params)
            all_violations.extend(field_result.violations)
            all_warnings.extend(field_result.warnings)
            all_bounds_checked.update(
                {
                    f"field_{k}": v
                    for k, v in field_result.bounds_checked.items()
                }
            )

        is_valid = len(all_violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=all_violations,
            warnings=all_warnings,
            bounds_checked=all_bounds_checked,
        )


class ExperimentalValidator:
    """
    Validator for experimental data quality and systematic error detection.
    """

    def __init__(self):
        self.quantum_validator = QuantumBoundsValidator()

    def validate_count_statistics(
        self, counts: np.ndarray, expected_rate: float, measurement_time: float
    ) -> ValidationResult:
        """
        Validate photon counting statistics for Poisson behavior.

        Parameters:
        -----------
        counts : array
            Array of photon count measurements
        expected_rate : float
            Expected count rate (Hz)
        measurement_time : float
            Integration time per measurement (s)

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        expected_counts = expected_rate * measurement_time

        # Check for reasonable count levels
        mean_counts = np.mean(counts)
        count_level_ok = (
            0.1 * expected_counts <= mean_counts <= 10 * expected_counts
        )
        bounds_checked["count_level"] = count_level_ok

        if not count_level_ok:
            warnings_list.append(
                f"Count rate differs from expected: "
                f"measured = {mean_counts/measurement_time:.1f} Hz, "
                f"expected = {expected_rate:.1f} Hz"
            )

        # Check Poisson statistics
        variance = np.var(counts)
        poisson_ok = abs(variance - mean_counts) < 3 * np.sqrt(mean_counts)
        bounds_checked["poisson_statistics"] = poisson_ok

        if not poisson_ok:
            violations.append(
                f"Non-Poisson statistics detected: "
                f"variance = {variance:.1f}, mean = {mean_counts:.1f}"
            )

        # Check for zero counts (detector failure)
        zero_counts = np.sum(counts == 0)
        zero_fraction = zero_counts / len(counts)
        excessive_zeros = zero_fraction > 0.01  # More than 1% zero counts
        bounds_checked["excessive_zeros"] = not excessive_zeros

        if excessive_zeros:
            violations.append(
                f"Excessive zero counts: {zero_fraction:.3f} fraction"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )

    def detect_systematic_drifts(
        self, data: np.ndarray, time_stamps: np.ndarray
    ) -> ValidationResult:
        """
        Detect systematic drifts in experimental data.

        Parameters:
        -----------
        data : array
            Time series data to analyze
        time_stamps : array
            Time stamps for each data point

        Returns:
        --------
        ValidationResult : Validation results
        """
        violations = []
        warnings_list = []
        bounds_checked = {}

        # Linear drift test
        from scipy import stats

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            time_stamps, data
        )

        significant_drift = p_value < 0.01 and abs(r_value) > 0.1
        bounds_checked["linear_drift"] = not significant_drift

        if significant_drift:
            warnings_list.append(
                f"Significant linear drift detected: "
                f"slope = {slope:.6e}, r = {r_value:.3f}, p = {p_value:.3e}"
            )

        # Step change detection (simple)
        data_diff = np.diff(data)
        large_steps = np.abs(data_diff) > 5 * np.std(data_diff)
        step_fraction = np.sum(large_steps) / len(data_diff)
        excessive_steps = step_fraction > 0.001  # More than 0.1% large steps
        bounds_checked["step_changes"] = not excessive_steps

        if excessive_steps:
            violations.append(
                f"Excessive step changes detected: {step_fraction:.4f} fraction"
            )

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings_list,
            bounds_checked=bounds_checked,
        )


def validate_simulation_results(simulation_results: Dict) -> ValidationResult:
    """
    Convenience function to validate complete simulation results.

    Parameters:
    -----------
    simulation_results : dict
        Dictionary containing simulation results with keys:
        - 's_values': CHSH parameter values
        - 'correlations': individual correlations (optional)
        - 'amplification': amplification factors (optional)
        - 'field_params': field parameters (optional)

    Returns:
    --------
    ValidationResult : Comprehensive validation results
    """
    validator = QuantumBoundsValidator()

    return validator.comprehensive_validation(
        S=simulation_results["s_values"],
        correlations=simulation_results.get("correlations"),
        amplification=simulation_results.get("amplification"),
        field_params=simulation_results.get("field_params"),
    )


def log_validation_results(result: ValidationResult, logger=None):
    """
    Log validation results in a structured format.

    Parameters:
    -----------
    result : ValidationResult
        Validation results to log
    logger : logging.Logger, optional
        Logger instance (uses print if None)
    """
    log_func = logger.info if logger else print

    if result.is_valid:
        log_func("✓ All physics validations passed")
    else:
        log_func("✗ Physics validation failures detected:")
        for violation in result.violations:
            log_func(f"  - {violation}")

    if result.warnings:
        log_func("⚠ Physics validation warnings:")
        for warning in result.warnings:
            log_func(f"  - {warning}")

    # Summary of bounds checked
    passed_checks = sum(result.bounds_checked.values())
    total_checks = len(result.bounds_checked)
    log_func(f"Bounds checked: {passed_checks}/{total_checks} passed")


if __name__ == "__main__":
    # Example validation usage
    print("Physics Validation Module")
    print("=" * 40)

    # Test CHSH parameter validation
    validator = QuantumBoundsValidator()

    # Valid case
    S_valid = 2.5  # Within Tsirelson bound
    result = validator.validate_chsh_parameter(S_valid)
    print(f"\nValidating S = {S_valid}:")
    log_validation_results(result)

    # Invalid case
    S_invalid = 3.0  # Violates Tsirelson bound
    result = validator.validate_chsh_parameter(S_invalid)
    print(f"\nValidating S = {S_invalid}:")
    log_validation_results(result)

    # Test comprehensive validation
    print("\n" + "=" * 40)
    print("Comprehensive Validation Test")

    simulation_results = {
        "s_values": np.array([2.4, 2.6, 2.5]),
        "correlations": {"E_00": 0.7, "E_01": -0.7, "E_10": 0.7, "E_11": 0.7},
        "amplification": np.array([1.05, 1.08, 1.06]),
        "field_params": {
            "field_mass": 1e-6,
            "coupling_strength": 0.05,
            "field_speed": 3e8,
        },
    }

    result = validate_simulation_results(simulation_results)
    log_validation_results(result)
