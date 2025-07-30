---
layout: default
title: Getting Started with EQFE
permalink: /getting-started/
---

# Getting Started with EQFE

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PelicansPerspective/Environmental-Quantum-Field-Effects.git
   cd Environmental-Quantum-Field-Effects
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -m pytest tests/ -v
   ```

## Quick Start

## Theory and Frameworks

Before running simulations, familiarize yourself with our theoretical foundations:

- [Multi-Scale Modeling Framework]({{ site.baseurl }}/multi-scale-framework/) - Our hierarchical approach connecting quantum field theory to observable effects
- [Experimental Validation Framework]({{ site.baseurl }}/experimental-validation/) - Protocols for testing EQFE predictions
- [Computational Tools]({{ site.baseurl }}/computational-tools/) - Advanced simulation capabilities
- [API Reference]({{ site.baseurl }}/api-reference/) - Complete API documentation and usage examples

### Basic Simulation

```python
from simulations.core import EnvironmentalFieldSimulator, CHSHExperimentSimulator
from simulations.core.multi_scale_simulation import EnvironmentalCorrelation, OpenQuantumSystem

# Option 1: Traditional Field Simulator
env_sim = EnvironmentalFieldSimulator(
    field_mass=1e-6,        # 1 μeV
    coupling_strength=1e-3,  # Weak coupling
    temperature=300.0        # Room temperature
)

# Set up Bell test experiment
chsh_sim = CHSHExperimentSimulator(env_sim)

# Run simulation
results = chsh_sim.simulate_bell_experiment(n_trials=10000)
print(f"CHSH parameter: {results['S_mean']:.4f} ± {results['S_std']:.4f}")

# Option 2: Advanced Multi-scale Simulator
env = EnvironmentalCorrelation(
    correlation_type='structured',
    correlation_time=2.0,
    coupling_strength=0.1,
    temperature=0.1
)

# Create demonstration of quantum correlation enhancement
amplifier = QuantumCorrelationAmplifier()
results = amplifier.demonstrate_eqfe()
```

### Parameter Optimization

```python
# Find optimal conditions for enhancement
temperatures = np.linspace(50, 400, 20)
enhancements = []

for T in temperatures:
    env_sim = EnvironmentalFieldSimulator(
        field_mass=1e-6,
        coupling_strength=1e-3,
        temperature=T
    )
    A = env_sim.amplification_factor(measurement_time=1e-6)
    enhancements.append(A)

optimal_temp = temperatures[np.argmax(enhancements)]
print(f"Optimal temperature: {optimal_temp:.1f} K")
```

## Examples

Run the included example scripts:

```bash
# Basic demonstration
python examples/basic_demo.py

# Advanced analysis
python examples/advanced_analysis.py
```

## Next Steps

- Review the [theory documentation](https://github.com/PelicansPerspective/Environmental-Quantum-Field-Effects/tree/main/theory) for mathematical details
- Check [experimental protocols](https://github.com/PelicansPerspective/Environmental-Quantum-Field-Effects/tree/main/experiments/protocols) for lab procedures  
- Explore the [API reference]({{ site.baseurl }}/api-reference/) for detailed usage
