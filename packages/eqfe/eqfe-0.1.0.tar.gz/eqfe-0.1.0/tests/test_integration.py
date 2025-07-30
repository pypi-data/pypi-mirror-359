"""
Integration Tests for EQFE Package

End-to-end tests validating complete workflows.
"""

import numpy as np
import sys
from pathlib import Path

# Add project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simulations.core.field_simulator import EnvironmentalFieldSimulator
from simulations.core.quantum_correlations import CHSHExperimentSimulator


class TestEQFEWorkflows:
    """Test complete EQFE analysis workflows."""

    def test_basic_demo_workflow(self):
        """Test the basic demonstration workflow works end-to-end."""
        # This mirrors the basic_demo.py script

        # 1. Basic simulation
        env_sim = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=1e-3, temperature=300.0
        )
        chsh_sim = CHSHExperimentSimulator(env_sim)
        results = chsh_sim.simulate_bell_experiment(n_trials=1000)

        # Validate results structure
        assert "S_mean" in results
        assert "S_std" in results
        assert isinstance(results["S_mean"], float)
        assert isinstance(results["S_std"], float)

        # Physics validation
        assert results["S_mean"] <= 2 * np.sqrt(2) + 1e-10
        assert results["S_std"] > 0

        # 2. Temperature optimization
        temperatures = np.linspace(100, 400, 5)
        chsh_values = []

        for T in temperatures:
            env_sim_T = EnvironmentalFieldSimulator(
                field_mass=1e-6, coupling_strength=1e-3, temperature=T
            )
            chsh_sim_T = CHSHExperimentSimulator(env_sim_T)
            results_T = chsh_sim_T.simulate_bell_experiment(n_trials=500)
            chsh_values.append(results_T["S_mean"])

        # Should have variation in CHSH values
        assert np.std(chsh_values) > 1e-6

        # 3. Time evolution
        times = np.logspace(-7, -5, 5)
        amplifications = []

        for t in times:
            A = env_sim.amplification_factor(t)
            amplifications.append(A)

        # Should have real, positive amplifications
        assert all(np.isreal(A) and A > 0 for A in amplifications)

    def test_parameter_space_exploration(self):
        """Test systematic parameter space exploration."""

        # Test parameter ranges
        field_masses = [1e-7, 1e-6, 1e-5]
        couplings = [1e-4, 1e-3, 1e-2]
        temperatures = [100, 300, 500]

        results_matrix = []

        for m in field_masses:
            for g in couplings:
                for T in temperatures:
                    try:
                        env_sim = EnvironmentalFieldSimulator(
                            field_mass=m, coupling_strength=g, temperature=T
                        )

                        # Test amplification calculation
                        A = env_sim.amplification_factor(1e-6)

                        # Test CHSH simulation
                        chsh_sim = CHSHExperimentSimulator(env_sim)
                        results = chsh_sim.simulate_bell_experiment(
                            n_trials=100
                        )

                        result_entry = {
                            "mass": m,
                            "coupling": g,
                            "temperature": T,
                            "amplification": A,
                            "chsh": results["S_mean"],
                        }
                        results_matrix.append(result_entry)

                    except Exception as e:
                        # Should not have exceptions for valid parameter ranges
                        assert (
                            False
                        ), f"Failed for params m={m}, g={g}, T={T}: {e}"

        # Should have results for all parameter combinations
        assert len(results_matrix) == len(field_masses) * len(couplings) * len(
            temperatures
        )

        # All results should respect physics bounds
        for result in results_matrix:
            assert result["amplification"] > 0
            assert result["chsh"] <= 2 * np.sqrt(2) + 1e-10

    def test_experimental_protocol_simulation(self):
        """Test realistic experimental protocol simulation."""

        # Simulate experimental conditions
        protocol_params = {
            "temperatures": [77, 200, 300, 400],
            "field_mass": 1e-6,
            "coupling_strength": 1e-3,
            "n_trials": 1000,
            "detection_efficiency": 0.8,
            "measurement_time": 1e-3,
        }

        experimental_results = {}

        for T in protocol_params["temperatures"]:
            env_sim = EnvironmentalFieldSimulator(
                field_mass=protocol_params["field_mass"],
                coupling_strength=protocol_params["coupling_strength"],
                temperature=T,
            )

            chsh_sim = CHSHExperimentSimulator(env_sim)
            results = chsh_sim.simulate_bell_experiment(
                n_trials=protocol_params["n_trials"]
            )

            # Apply experimental imperfections
            detection_eff = protocol_params["detection_efficiency"]
            S_corrected = results["S_mean"] * detection_eff**2

            experimental_results[T] = {
                "S_ideal": results["S_mean"],
                "S_experimental": S_corrected,
                "uncertainty": results["S_std"],
            }

        # Validate experimental results
        for T, result in experimental_results.items():
            # Experimental values should be lower than ideal
            assert result["S_experimental"] <= result["S_ideal"]

            # Should still respect bounds
            assert result["S_experimental"] <= 2 * np.sqrt(2) + 1e-10

            # Should have reasonable uncertainties
            assert 0 < result["uncertainty"] < 1.0

    def test_physics_consistency_across_scales(self):
        """Test physics consistency across different parameter scales."""

        # Test multiple scales
        scales = [
            {"mass": 1e-8, "coupling": 1e-4, "temp": 10},  # Low energy
            {"mass": 1e-6, "coupling": 1e-3, "temp": 300},  # Standard
            {"mass": 1e-4, "coupling": 1e-2, "temp": 1000},  # High energy
        ]

        for i, params in enumerate(scales):
            env_sim = EnvironmentalFieldSimulator(
                field_mass=params["mass"],
                coupling_strength=params["coupling"],
                temperature=params["temp"],
            )

            # Test different time scales
            times = np.logspace(-9, -3, 10)

            for t in times:
                A = env_sim.amplification_factor(t)

                # Physics consistency checks
                assert np.isreal(
                    A
                ), f"Non-real amplification at scale {i}, time {t}"
                assert (
                    A > 0
                ), f"Non-positive amplification at scale {i}, time {t}"
                assert (
                    A < 10
                ), f"Unphysically large amplification at scale {i}, time {t}"

            # Test CHSH bounds
            chsh_sim = CHSHExperimentSimulator(env_sim)
            results = chsh_sim.simulate_bell_experiment(n_trials=500)

            S = results["S_mean"]
            assert (
                S <= 2 * np.sqrt(2) + 1e-10
            ), f"Tsirelson violation at scale {i}: S={S}"


def test_full_validation_suite():
    """Run complete validation of EQFE implementation."""

    print("Running full EQFE validation suite...")

    # Initialize test suite
    test_suite = TestEQFEWorkflows()

    # Run all tests
    test_methods = [
        test_suite.test_basic_demo_workflow,
        test_suite.test_parameter_space_exploration,
        test_suite.test_experimental_protocol_simulation,
        test_suite.test_physics_consistency_across_scales,
    ]

    for test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_method.__name__}")
        except Exception as e:
            print(f"❌ {test_method.__name__}: {e}")
            raise

    print("🎉 Full validation suite passed!")


if __name__ == "__main__":
    test_full_validation_suite()
