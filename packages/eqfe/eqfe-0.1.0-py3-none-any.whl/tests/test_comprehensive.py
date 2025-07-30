"""
Test Suite for Environmental Quantum Field Effects

This module contains comprehensive tests for all simulation and analysis components
to ensure correctness, physics compliance, and numerical stability.
"""

import unittest
import numpy as np
import numpy.testing as npt
from unittest.mock import Mock, patch
import warnings

# Import modules to test
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "simulations"))

try:
    from simulations.core.field_simulator import (
        EnvironmentalFieldSimulator,
        PhysicalConstants,
    )
    from simulations.core.quantum_correlations import CHSHExperimentSimulator
    from simulations.analysis.physics_validator import (
        QuantumBoundsValidator,
        ValidationResult,
    )
    from simulations.analysis.experimental_analysis import (
        CHSHAnalyzer,
        EnvironmentalCorrelationAnalyzer,
    )
except ImportError as e:
    print(f"Warning: Could not import modules for testing: {e}")
    pytest.skip("Required modules not available", allow_module_level=True)


class TestPhysicalConstants:
    """Test physical constants and their consistency."""

    def test_speed_of_light(self):
        """Test speed of light constant."""
        assert PhysicalConstants.c == 299792458.0

    def test_hbar(self):
        """Test reduced Planck constant."""
        assert PhysicalConstants.hbar == 1.054571817e-34

    def test_electromagnetic_constants(self):
        """Test consistency of electromagnetic constants."""
        # Test c = 1/√(μ₀ε₀)
        c_derived = 1.0 / np.sqrt(
            PhysicalConstants.mu_0 * PhysicalConstants.epsilon_0
        )
        npt.assert_allclose(c_derived, PhysicalConstants.c, rtol=1e-10)


class TestQuantumBoundsValidator:
    """Test quantum mechanical bounds validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = QuantumBoundsValidator()

    def test_tsirelson_bound_valid(self):
        """Test valid CHSH values within Tsirelson bound."""
        S_valid = np.array([2.0, 2.5, 2.828])
        result = self.validator.validate_chsh_parameter(S_valid)

        assert result.is_valid
        assert len(result.violations) == 0
        assert result.bounds_checked["tsirelson"]

    def test_tsirelson_bound_violation(self):
        """Test detection of Tsirelson bound violations."""
        S_invalid = np.array([3.0, 3.5])
        result = self.validator.validate_chsh_parameter(S_invalid)

        assert not result.is_valid
        assert len(result.violations) > 0
        assert not result.bounds_checked["tsirelson"]
        assert "Tsirelson bound violated" in result.violations[0]

    def test_classical_bound_detection(self):
        """Test detection of quantum advantage."""
        S_quantum = np.array([2.5, 2.7])
        result = self.validator.validate_chsh_parameter(S_quantum)

        assert result.bounds_checked["quantum_advantage"]

        S_classical = np.array([1.8, 1.9])
        result = self.validator.validate_chsh_parameter(S_classical)

        assert not result.bounds_checked["quantum_advantage"]

    def test_negative_chsh_values(self):
        """Test detection of non-physical negative CHSH values."""
        S_negative = np.array([-0.5, 2.0])
        result = self.validator.validate_chsh_parameter(S_negative)

        assert not result.is_valid
        assert not result.bounds_checked["positivity"]

    def test_correlation_bounds(self):
        """Test correlation function bounds."""
        correlations_valid = {
            "E_00": 0.7,
            "E_01": -0.5,
            "E_10": 0.3,
            "E_11": -0.8,
        }
        result = self.validator.validate_correlations(correlations_valid)

        assert result.is_valid
        assert result.bounds_checked["correlation_bounds"]

        correlations_invalid = {"E_00": 1.5, "E_01": -0.5}
        result = self.validator.validate_correlations(correlations_invalid)

        assert not result.is_valid
        assert not result.bounds_checked["correlation_bounds"]

    def test_probability_validation(self):
        """Test probability distribution validation."""
        # Valid probabilities
        probs_valid = np.array([0.25, 0.25, 0.25, 0.25])
        result = self.validator.validate_probabilities(probs_valid)

        assert result.is_valid
        assert result.bounds_checked["positivity"]
        assert result.bounds_checked["normalization"]
        assert result.bounds_checked["probability_bounds"]

        # Invalid probabilities (negative)
        probs_negative = np.array([-0.1, 0.6, 0.3, 0.2])
        result = self.validator.validate_probabilities(probs_negative)

        assert not result.is_valid
        assert not result.bounds_checked["positivity"]

        # Invalid probabilities (not normalized)
        probs_unnormalized = np.array([0.3, 0.3, 0.3, 0.3])
        result = self.validator.validate_probabilities(probs_unnormalized)

        assert not result.is_valid
        assert not result.bounds_checked["normalization"]


class TestEnvironmentalFieldSimulator:
    """Test environmental field simulator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.simulator = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=0.01, temperature=300.0
        )

    def test_initialization(self):
        """Test proper initialization of simulator."""
        assert self.simulator.field_mass == 1e-6
        assert self.simulator.coupling_strength == 0.01
        assert self.simulator.temperature == 300.0
        assert self.simulator.field_speed == PhysicalConstants.c

    def test_parameter_validation(self):
        """Test parameter validation on initialization."""
        # Valid parameters should not raise errors
        EnvironmentalFieldSimulator(field_mass=1e-6, coupling_strength=0.01)

        # Invalid parameters should raise errors
        with pytest.raises(ValueError):
            EnvironmentalFieldSimulator(field_mass=-1.0)

        with pytest.raises(ValueError):
            EnvironmentalFieldSimulator(coupling_strength=-0.1)

        with pytest.raises(ValueError):
            EnvironmentalFieldSimulator(temperature=-10.0)

    def test_field_fluctuations_shape(self):
        """Test shape of generated field fluctuations."""
        n_samples = 1000
        fluctuations = self.simulator.thermal_field_fluctuations(n_samples)

        assert fluctuations.shape == (n_samples,)
        assert np.isfinite(fluctuations).all()

    def test_field_fluctuations_statistics(self):
        """Test statistical properties of field fluctuations."""
        n_samples = 10000
        fluctuations = self.simulator.thermal_field_fluctuations(n_samples)

        # Should have zero mean (approximately)
        mean = np.mean(fluctuations)
        assert abs(mean) < 0.1

        # Should have positive variance
        variance = np.var(fluctuations)
        assert variance > 0

    def test_correlation_modification(self):
        """Test quantum correlation modification."""
        ideal_chsh = 2 * np.sqrt(2)
        field_data = np.random.normal(0, 1, 100)
        measurement_time = 1.0

        modified_chsh = self.simulator.modify_quantum_correlations(
            ideal_chsh, field_data, measurement_time
        )

        assert modified_chsh.shape == field_data.shape
        assert np.isfinite(modified_chsh).all()

    def test_amplification_bounds(self):
        """Test that amplification respects physical bounds."""
        ideal_chsh = 2.5
        field_data = np.random.normal(0, 0.1, 100)  # Small fluctuations
        measurement_time = 0.1  # Short time

        modified_chsh = self.simulator.modify_quantum_correlations(
            ideal_chsh, field_data, measurement_time
        )

        # Should not grossly violate Tsirelson bound
        tsirelson_bound = 2 * np.sqrt(2)
        violation_fraction = np.mean(modified_chsh > tsirelson_bound * 1.1)
        assert violation_fraction < 0.1  # Less than 10% violations


class TestCHSHExperimentSimulator:
    """Test CHSH experiment simulation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.env_simulator = EnvironmentalFieldSimulator()
        self.chsh_simulator = CHSHExperimentSimulator(self.env_simulator)

    def test_initialization(self):
        """Test proper initialization."""
        assert self.chsh_simulator.env_simulator is self.env_simulator
        assert self.chsh_simulator.tsirelson_bound == 2 * np.sqrt(2)
        assert self.chsh_simulator.classical_bound == 2.0

    def test_ideal_quantum_correlation(self):
        """Test ideal quantum correlation value."""
        ideal_chsh = self.chsh_simulator.ideal_quantum_correlation()
        expected = 2 * np.sqrt(2)

        npt.assert_allclose(ideal_chsh, expected, rtol=1e-10)

    def test_bell_experiment_simulation(self):
        """Test complete Bell experiment simulation."""
        n_trials = 1000
        result = self.chsh_simulator.simulate_bell_experiment(
            n_trials=n_trials
        )

        # Check result structure
        assert "chsh_values" in result
        assert "environmental_amplification" in result
        assert "measurement_statistics" in result
        assert "validation_results" in result

        # Check data shapes
        assert result["chsh_values"].shape == (n_trials,)
        assert len(result["environmental_amplification"]) == n_trials

        # Check physics validation
        assert result["validation_results"].is_valid

    def test_measurement_noise_effect(self):
        """Test effect of measurement noise."""
        n_trials = 500

        # No noise
        result_no_noise = self.chsh_simulator.simulate_bell_experiment(
            n_trials=n_trials, measurement_noise=0.0
        )

        # With noise
        result_with_noise = self.chsh_simulator.simulate_bell_experiment(
            n_trials=n_trials, measurement_noise=0.1
        )

        # Noise should increase variance
        var_no_noise = np.var(result_no_noise["chsh_values"])
        var_with_noise = np.var(result_with_noise["chsh_values"])

        assert var_with_noise > var_no_noise


class TestCHSHAnalyzer:
    """Test CHSH data analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CHSHAnalyzer()

    def test_chsh_calculation(self):
        """Test CHSH parameter calculation from correlations."""
        # Perfect quantum correlations
        correlations = {
            "E_00": 1 / np.sqrt(2),
            "E_01": -1 / np.sqrt(2),
            "E_10": 1 / np.sqrt(2),
            "E_11": 1 / np.sqrt(2),
        }

        S = self.analyzer.calculate_chsh_parameter(correlations)
        expected = 2 * np.sqrt(2)

        npt.assert_allclose(S, expected, rtol=1e-10)

    def test_missing_correlation_data(self):
        """Test handling of missing correlation data."""
        incomplete_correlations = {"E_00": 0.5, "E_01": -0.5}

        with pytest.raises(ValueError):
            self.analyzer.calculate_chsh_parameter(incomplete_correlations)

    def test_correlation_from_counts(self):
        """Test correlation calculation from count data."""
        # Mock count data for perfect anti-correlation
        counts = {
            "AB_00_pp": np.array([100]),
            "AB_00_pm": np.array([0]),
            "AB_00_mp": np.array([0]),
            "AB_00_mm": np.array([100]),
            "AB_01_pp": np.array([0]),
            "AB_01_pm": np.array([100]),
            "AB_01_mp": np.array([100]),
            "AB_01_mm": np.array([0]),
        }

        correlations = self.analyzer.correlation_from_counts(counts)

        assert "E_00" in correlations
        assert correlations["E_00"][0] == 1.0  # Perfect correlation

        if "E_01" in correlations:
            assert correlations["E_01"][0] == -1.0  # Perfect anti-correlation


class TestEnvironmentalCorrelationAnalyzer:
    """Test environmental correlation analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EnvironmentalCorrelationAnalyzer()

    def test_field_variance_calculation(self):
        """Test field variance calculation."""
        n_points = 200
        field_data = np.random.normal(0, 1, n_points)

        variance = self.analyzer.calculate_field_variance(
            field_data, window_size=50
        )

        assert variance.shape == (n_points,)
        assert np.all(variance >= 0)  # Variance must be non-negative
        assert np.isfinite(variance).all()

    def test_correlation_analysis(self):
        """Test correlation analysis between CHSH and field variance."""
        n_points = 500

        # Generate correlated data
        field_variance = np.random.exponential(1.0, n_points)
        chsh_values = (
            2.0 + 0.3 * field_variance + np.random.normal(0, 0.1, n_points)
        )

        result = self.analyzer.correlation_analysis(
            chsh_values, field_variance
        )

        assert "correlation_coefficient" in result
        assert "p_value" in result
        assert "is_significant" in result
        assert "effect_size" in result

        # Should detect positive correlation
        assert result["correlation_coefficient"] > 0

    def test_lag_correlation_analysis(self):
        """Test time-lagged correlation analysis."""
        n_points = 200
        max_lag = 20

        # Generate data with known lag
        field_variance = np.random.exponential(1.0, n_points)
        chsh_values = np.zeros(n_points)
        chsh_values[5:] = 0.3 * field_variance[:-5]  # 5-step lag
        chsh_values += np.random.normal(0, 0.1, n_points)

        result = self.analyzer.lag_correlation_analysis(
            chsh_values, field_variance, max_lag=max_lag
        )

        assert "lags" in result
        assert "correlations" in result
        assert "optimal_lag" in result

        # Should detect the 5-step lag (approximately)
        assert abs(result["optimal_lag"] - 5) <= 2


class TestIntegration:
    """Integration tests for complete simulation pipeline."""

    def test_full_simulation_pipeline(self):
        """Test complete simulation from field generation to analysis."""
        # Create simulator
        env_simulator = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=0.05, temperature=300.0
        )

        chsh_simulator = CHSHExperimentSimulator(env_simulator)

        # Run simulation
        n_trials = 1000
        results = chsh_simulator.simulate_bell_experiment(n_trials=n_trials)

        # Validate results
        validator = QuantumBoundsValidator()
        validation = validator.validate_chsh_parameter(results["chsh_values"])

        assert (
            validation.is_valid
        ), f"Physics validation failed: {validation.violations}"

        # Analyze results
        analyzer = CHSHAnalyzer()
        env_analyzer = EnvironmentalCorrelationAnalyzer()

        # Calculate field variance
        field_variance = env_analyzer.calculate_field_variance(
            results.get("field_data", np.random.normal(0, 1, n_trials))
        )

        # Test correlation analysis
        correlation_result = env_analyzer.correlation_analysis(
            results["chsh_values"], field_variance
        )

        assert "correlation_coefficient" in correlation_result

    def test_consistency_across_parameter_ranges(self):
        """Test consistency across different parameter ranges."""
        coupling_strengths = [0.001, 0.01, 0.05]
        field_masses = [1e-7, 1e-6, 1e-5]

        for g in coupling_strengths:
            for m in field_masses:
                # Should not raise exceptions for reasonable parameters
                simulator = EnvironmentalFieldSimulator(
                    field_mass=m, coupling_strength=g, temperature=300.0
                )

                # Test field generation
                field_data = simulator.thermal_field_fluctuations(100)
                assert np.isfinite(field_data).all()

                # Test correlation modification
                modified_chsh = simulator.modify_quantum_correlations(
                    2.4, field_data, 1.0
                )
                assert np.isfinite(modified_chsh).all()


class TestNumericalStability:
    """Test numerical stability and edge cases."""

    def test_small_coupling_limit(self):
        """Test behavior in small coupling limit."""
        simulator = EnvironmentalFieldSimulator(coupling_strength=1e-10)

        field_data = simulator.thermal_field_fluctuations(100)
        modified_chsh = simulator.modify_quantum_correlations(
            2.4, field_data, 1.0
        )

        # Should be very close to unmodified value
        npt.assert_allclose(modified_chsh, 2.4, rtol=1e-6)

    def test_zero_temperature_limit(self):
        """Test behavior at zero temperature."""
        # Use very small but non-zero temperature to avoid division by zero
        simulator = EnvironmentalFieldSimulator(temperature=1e-10)

        field_data = simulator.thermal_field_fluctuations(100)

        # Should have very small fluctuations
        assert np.var(field_data) < 1e-6

    def test_large_field_values(self):
        """Test handling of large field values."""
        simulator = EnvironmentalFieldSimulator()

        # Large field values
        large_field = np.full(100, 1000.0)

        # Should handle gracefully (may saturate amplification)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            modified_chsh = simulator.modify_quantum_correlations(
                2.4, large_field, 1.0
            )

        assert np.isfinite(modified_chsh).all()

    def test_empty_arrays(self):
        """Test handling of empty input arrays."""
        simulator = EnvironmentalFieldSimulator()
        analyzer = CHSHAnalyzer()

        # Empty field data
        empty_field = np.array([])
        result = simulator.modify_quantum_correlations(2.4, empty_field, 1.0)

        assert result.shape == (0,)


# Performance benchmarks (optional, run with pytest-benchmark if available)
class TestPerformance:
    """Performance benchmarks for critical functions."""

    @pytest.mark.skipif(
        not pytest.importorskip("pytest_benchmark", minversion="3.0.0"),
        reason="pytest-benchmark not available",
    )
    def test_field_generation_performance(self, benchmark):
        """Benchmark field generation performance."""
        simulator = EnvironmentalFieldSimulator()

        def generate_field():
            return simulator.thermal_field_fluctuations(10000)

        result = benchmark(generate_field)
        assert len(result) == 10000

    @pytest.mark.skipif(
        not pytest.importorskip("pytest_benchmark", minversion="3.0.0"),
        reason="pytest-benchmark not available",
    )
    def test_correlation_modification_performance(self, benchmark):
        """Benchmark correlation modification performance."""
        simulator = EnvironmentalFieldSimulator()
        field_data = np.random.normal(0, 1, 10000)

        def modify_correlations():
            return simulator.modify_quantum_correlations(2.4, field_data, 1.0)

        result = benchmark(modify_correlations)
        assert len(result) == 10000


if __name__ == "__main__":
    # Run basic tests if called directly
    print("Running Environmental Quantum Field Effects Test Suite")
    print("=" * 60)

    # Run a subset of tests manually if pytest is not available
    try:
        # Test physical constants
        test_constants = TestPhysicalConstants()
        test_constants.test_speed_of_light()
        test_constants.test_electromagnetic_constants()
        print("✓ Physical constants tests passed")

        # Test validator
        test_validator = TestQuantumBoundsValidator()
        test_validator.setup_method()
        test_validator.test_tsirelson_bound_valid()
        test_validator.test_tsirelson_bound_violation()
        print("✓ Quantum bounds validator tests passed")

        # Test simulator
        test_simulator = TestEnvironmentalFieldSimulator()
        test_simulator.setup_method()
        test_simulator.test_initialization()
        test_simulator.test_field_fluctuations_shape()
        test_simulator.test_amplification_bounds()
        print("✓ Environmental field simulator tests passed")

        print("\nBasic test suite completed successfully!")
        print("Run 'pytest' for complete test coverage")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
