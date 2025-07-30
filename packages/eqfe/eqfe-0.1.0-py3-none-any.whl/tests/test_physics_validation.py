"""
Physics Validation Tests

Comprehensive test suite to ensure all quantum correlations respect
fundamental physics principles and bounds.
"""

import numpy as np
import pytest
from hypothesis import given, strategies as st

from simulations.core.field_simulator import (
    EnvironmentalFieldSimulator,
    QuantumBoundValidator,
    PhysicalConstants,
)
from simulations.core.quantum_correlations import CHSHExperimentSimulator


class TestQuantumBounds:
    """Test fundamental quantum mechanical bounds."""

    def test_tsirelson_bound_respected(self):
        """Test that CHSH parameter never exceeds Tsirelson bound."""
        # Test with various environmental conditions
        test_conditions = [
            {
                "field_mass": 1e-6,
                "coupling_strength": 1e-3,
                "temperature": 300.0,
            },
            {
                "field_mass": 1e-5,
                "coupling_strength": 1e-4,
                "temperature": 77.0,
            },
            {
                "field_mass": 1e-4,
                "coupling_strength": 1e-2,
                "temperature": 4.2,
            },
        ]

        for params in test_conditions:
            env_sim = EnvironmentalFieldSimulator(**params)
            chsh_sim = CHSHExperimentSimulator(env_sim)

            results = chsh_sim.simulate_bell_experiment(n_trials=1000)

            # Check Tsirelson bound
            assert QuantumBoundValidator.check_tsirelson_bound(
                results["S_mean"]
            )
            assert results["S_mean"] <= 2 * np.sqrt(2) + 1e-10

    @given(
        field_mass=st.floats(min_value=1e-8, max_value=1e-2),
        coupling=st.floats(min_value=1e-5, max_value=1e-1),
        temperature=st.floats(min_value=0.1, max_value=1000.0),
    )
    def test_physics_bounds_property_based(
        self, field_mass, coupling, temperature
    ):
        """Property-based test for physics bounds."""
        env_sim = EnvironmentalFieldSimulator(
            field_mass=field_mass,
            coupling_strength=coupling,
            temperature=temperature,
        )

        # Generate amplification factor
        A = env_sim.amplification_factor(measurement_time=1e-6)

        # Amplification should be real and positive
        assert np.isreal(A)
        assert A > 0

        # For weak coupling, should be close to 1
        if coupling < 1e-3:
            assert abs(A - 1.0) < 0.1


class TestAmplificationLaw:
    """Test the theoretical amplification law implementation."""

    def test_amplification_law_formula(self):
        """Test amplification law mathematical formula."""
        env_sim = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=1e-3, temperature=300.0
        )

        t = 1e-6  # 1 microsecond
        A = env_sim.amplification_factor(t)

        # Manual calculation
        alpha = env_sim.coupling_strength**2 / 2
        beta = env_sim.coupling_strength**4 / 4
        field_variance = env_sim._calculate_field_variance()
        correlation_integral = env_sim._calculate_correlation_integral(t)

        expected_A = np.exp(
            alpha * field_variance * t - beta * correlation_integral
        )

        assert abs(A - expected_A) < 1e-10

    def test_time_evolution(self):
        """Test non-monotonic time evolution."""
        env_sim = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=1e-3, temperature=300.0
        )

        times = np.logspace(-9, -3, 50)  # 1 ns to 1 ms
        amplifications = [env_sim.amplification_factor(t) for t in times]

        # Should show initial enhancement then decay
        max_idx = np.argmax(amplifications)
        assert max_idx > 0  # Not at the beginning
        assert max_idx < len(amplifications) - 1  # Not at the end
        assert max(amplifications) > 1.0  # Shows enhancement

    def test_temperature_optimum(self):
        """Test temperature optimization prediction."""
        field_mass = 1e-6
        coupling = 1e-3
        temperatures = np.linspace(1.0, 1000.0, 100)

        enhancements = []
        for T in temperatures:
            env_sim = EnvironmentalFieldSimulator(
                field_mass=field_mass,
                coupling_strength=coupling,
                temperature=T,
            )
            A = env_sim.amplification_factor(1e-6)
            enhancements.append(A)

        # Should have a maximum somewhere in the range
        max_enhancement = max(enhancements)
        assert max_enhancement > 1.0

        # Find optimal temperature
        opt_idx = np.argmax(enhancements)
        T_opt = temperatures[opt_idx]
        assert 10.0 < T_opt < 900.0  # Reasonable range


class TestCHSHExperiment:
    """Test CHSH Bell test simulation implementation."""

    def test_standard_quantum_limit(self):
        """Test that without environmental effects, we get standard QM results."""
        # Zero coupling should give standard quantum results
        env_sim = EnvironmentalFieldSimulator(
            field_mass=1e-6,
            coupling_strength=0.0,  # No environmental coupling
            temperature=300.0,
        )
        chsh_sim = CHSHExperimentSimulator(env_sim)

        results = chsh_sim.simulate_bell_experiment(n_trials=10000)

        # Should be close to maximum quantum violation
        expected_S = 2 * np.sqrt(2)
        assert abs(results["S_mean"] - expected_S) < 0.1

    def test_statistical_properties(self):
        """Test statistical properties of Bell test results."""
        env_sim = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=1e-3, temperature=300.0
        )
        chsh_sim = CHSHExperimentSimulator(env_sim)

        # Run multiple experiments
        results_list = []
        for _ in range(10):
            results = chsh_sim.simulate_bell_experiment(n_trials=1000)
            results_list.append(results["S_mean"])

        # Check statistical consistency
        mean_S = np.mean(results_list)
        std_S = np.std(results_list)

        assert std_S > 0  # Should have some variation
        assert std_S < 0.5  # But not too much
        assert QuantumBoundValidator.check_tsirelson_bound(mean_S)


class TestPhysicalConstants:
    """Test physical constants and unit consistency."""

    def test_fundamental_constants(self):
        """Test that fundamental constants are correct."""
        pc = PhysicalConstants()

        # Speed of light
        assert abs(pc.c - 299792458.0) < 1e-6

        # Planck constant
        assert abs(pc.hbar - 1.054571817e-34) < 1e-44

        # Boltzmann constant
        assert abs(pc.k_B - 1.380649e-23) < 1e-33

        # Check derived relations
        assert abs(pc.epsilon_0 * pc.mu_0 * pc.c**2 - 1.0) < 1e-10


def validate_physics_bounds(results):
    """
    Comprehensive physics validation function.

    Parameters:
    -----------
    results : dict
        Bell test experiment results

    Raises:
    -------
    AssertionError : If any physics bound is violated
    """
    S = results["S_mean"]

    # Tsirelson bound
    assert QuantumBoundValidator.check_tsirelson_bound(
        S
    ), f"Tsirelson bound violated: S={S:.6f} > {2*np.sqrt(2):.6f}"

    # Classical bound (may be violated)
    if S > 2.0:
        print(f"Bell inequality violated: S={S:.6f} > 2 (quantum behavior)")

    # Correlation functions should be normalized
    if "correlations" in results:
        for corr in results["correlations"].values():
            assert -1.0 <= corr <= 1.0, f"Correlation out of bounds: {corr}"

    print("✅ All physics bounds respected")


if __name__ == "__main__":
    # Run basic validation
    env_sim = EnvironmentalFieldSimulator(
        field_mass=1e-6, coupling_strength=1e-3, temperature=300.0
    )
    chsh_sim = CHSHExperimentSimulator(env_sim)
    results = chsh_sim.simulate_bell_experiment(n_trials=1000)

    validate_physics_bounds(results)
    print(f"CHSH parameter: {results['S_mean']:.4f} ± {results['S_std']:.4f}")
