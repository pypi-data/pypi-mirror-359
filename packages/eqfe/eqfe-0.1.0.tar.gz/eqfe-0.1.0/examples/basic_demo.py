#!/usr/bin/env python3
"""
Basic EQFE Demonstration Script

This script demonstrates the core functionality of the Environmental Quantum
Field Effects simulation framework and validates key theoretical predictions.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simulations.core.field_simulator import EnvironmentalFieldSimulator
from simulations.core.quantum_correlations import CHSHExperimentSimulator
from tests.test_physics_validation import validate_physics_bounds


def main():
    """Run basic EQFE demonstration."""
    print("🌟 Environmental Quantum Field Effects - Basic Demo")
    print("=" * 60)

    # 1. Basic simulation with standard parameters
    print("\n1. Basic Simulation")
    print("-" * 20)

    env_sim = EnvironmentalFieldSimulator(
        field_mass=1e-6,  # 1 μeV field mass
        coupling_strength=1e-3,  # Weak coupling regime
        temperature=300.0,  # Room temperature
    )

    chsh_sim = CHSHExperimentSimulator(env_sim)

    # Run Bell test simulation
    print("Running Bell test simulation...")
    results = chsh_sim.simulate_bell_experiment(n_trials=10000)

    print(f"CHSH Parameter: {results['S_mean']:.4f} ± {results['S_std']:.4f}")
    print(f"Classical bound: S ≤ 2.000")
    print(f"Tsirelson bound: S ≤ {2*np.sqrt(2):.4f}")

    if results["S_mean"] > 2.0:
        print("✅ Bell inequality violated (quantum behavior)")
    else:
        print("❌ No Bell violation detected")

    # Validate physics bounds
    validate_physics_bounds(results)

    # 2. Temperature optimization study
    print("\n2. Temperature Optimization")
    print("-" * 30)

    temperatures = np.linspace(10, 500, 20)
    chsh_values = []

    print("Scanning temperature range...")
    for T in temperatures:
        env_sim_T = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=1e-3, temperature=T
        )
        chsh_sim_T = CHSHExperimentSimulator(env_sim_T)
        results_T = chsh_sim_T.simulate_bell_experiment(n_trials=1000)
        chsh_values.append(results_T["S_mean"])

    # Find optimal temperature
    max_idx = np.argmax(chsh_values)
    T_opt = temperatures[max_idx]
    S_max = chsh_values[max_idx]

    print(f"Optimal temperature: {T_opt:.1f} K")
    print(f"Maximum CHSH value: {S_max:.4f}")
    print(f"Enhancement factor: {S_max / (2*np.sqrt(2)):.4f}")

    # 3. Time evolution study
    print("\n3. Time Evolution Dynamics")
    print("-" * 30)

    # Set up for optimal conditions
    env_sim_opt = EnvironmentalFieldSimulator(
        field_mass=1e-6, coupling_strength=1e-3, temperature=T_opt
    )

    times = np.logspace(-7, -4, 15)  # 100 ns to 100 μs
    amplifications = []

    print("Studying time evolution...")
    for t in times:
        A = env_sim_opt.amplification_factor(t)
        amplifications.append(A)

    # Find enhancement regime
    max_A_idx = np.argmax(amplifications)
    t_opt = times[max_A_idx]
    A_max = amplifications[max_A_idx]

    print(f"Optimal measurement time: {t_opt*1e6:.1f} μs")
    print(f"Maximum amplification: {A_max:.4f}")

    if A_max > 1.0:
        print("✅ Enhancement detected in optimal regime")
    else:
        print("❌ No enhancement found")

    # 4. Coupling strength scaling
    print("\n4. Coupling Strength Scaling")
    print("-" * 35)

    couplings = np.logspace(-4, -2, 10)
    enhancements = []

    print("Testing coupling strength dependence...")
    for g in couplings:
        env_sim_g = EnvironmentalFieldSimulator(
            field_mass=1e-6, coupling_strength=g, temperature=T_opt
        )
        A = env_sim_g.amplification_factor(t_opt)
        enhancements.append(A - 1)  # Enhancement above baseline

    # Check g² scaling for weak coupling
    weak_mask = couplings < 5e-3
    if np.sum(weak_mask) > 3:
        # Fit to g² in weak coupling regime
        g_weak = couplings[weak_mask]
        enh_weak = np.array(enhancements)[weak_mask]

        # Linear fit in log-log space should give slope ≈ 2
        log_g = np.log10(g_weak)
        log_enh = np.log10(np.maximum(enh_weak, 1e-10))

        if len(log_g) > 2:
            slope = np.polyfit(log_g, log_enh, 1)[0]
            print(f"Coupling scaling exponent: {slope:.2f}")
            print(f"Expected g² scaling: 2.00")

            if abs(slope - 2.0) < 0.5:
                print("✅ g² scaling confirmed")
            else:
                print("⚠️  Scaling differs from g² expectation")

    # 5. Generate summary plots
    print("\n5. Generating Summary Plots")
    print("-" * 30)

    create_summary_plots(
        temperatures,
        chsh_values,
        times,
        amplifications,
        couplings,
        enhancements,
    )

    print("\n🎉 Demo completed successfully!")
    print("Check the generated plots for visual results.")


def create_summary_plots(
    temperatures, chsh_values, times, amplifications, couplings, enhancements
):
    """Create summary plots of key results."""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # Temperature optimization
    ax1.plot(temperatures, chsh_values, "b-o", markersize=4)
    ax1.axhline(y=2.0, color="r", linestyle="--", label="Classical bound")
    ax1.axhline(
        y=2 * np.sqrt(2), color="g", linestyle="--", label="Tsirelson bound"
    )
    ax1.set_xlabel("Temperature (K)")
    ax1.set_ylabel("CHSH Parameter S")
    ax1.set_title("Temperature Optimization")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Time evolution
    ax2.semilogx(times * 1e6, amplifications, "r-o", markersize=4)
    ax2.axhline(y=1.0, color="k", linestyle="--", alpha=0.5, label="Baseline")
    ax2.set_xlabel("Time (μs)")
    ax2.set_ylabel("Amplification Factor A")
    ax2.set_title("Time Evolution Dynamics")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Coupling scaling
    ax3.loglog(couplings, np.maximum(enhancements, 1e-6), "g-o", markersize=4)
    # Add g² reference line
    g_ref = np.logspace(-4, -2, 10)
    enhancement_ref = 1e2 * g_ref**2  # Arbitrary scaling for reference
    ax3.loglog(g_ref, enhancement_ref, "k--", alpha=0.5, label="g² scaling")
    ax3.set_xlabel("Coupling Strength g")
    ax3.set_ylabel("Enhancement (A - 1)")
    ax3.set_title("Coupling Strength Scaling")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Physics bounds verification
    S_values = np.array(chsh_values)
    ax4.hist(S_values, bins=15, alpha=0.7, color="blue", edgecolor="black")
    ax4.axvline(
        x=2.0, color="r", linestyle="--", linewidth=2, label="Classical bound"
    )
    ax4.axvline(
        x=2 * np.sqrt(2),
        color="g",
        linestyle="--",
        linewidth=2,
        label="Tsirelson bound",
    )
    ax4.set_xlabel("CHSH Parameter S")
    ax4.set_ylabel("Frequency")
    ax4.set_title("Physics Bounds Verification")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("eqfe_demo_results.png", dpi=300, bbox_inches="tight")
    print("Summary plots saved as 'eqfe_demo_results.png'")


if __name__ == "__main__":
    main()
