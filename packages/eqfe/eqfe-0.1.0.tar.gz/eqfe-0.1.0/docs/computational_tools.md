# Computational Tools

The Environmental Quantum Field Effects (EQFE) framework now includes advanced simulation tools to model quantum correlation enhancement across multiple parameter regimes.

## API Documentation

For detailed information about using the computational tools and hardware interfaces, please refer to our [Complete API Reference]({{ site.baseurl }}/api-reference/).

## Multi-Scale Simulation Framework

Our new simulation framework bridges microscopic quantum field theory with experimentally observable effects through:

### Environmental Correlation Models

- Multiple correlation function types (Ohmic, structured, custom)
- Temperature-dependent spectral densities
- Parameter scanning capabilities

<div class="visualization-container">
  <h3>Interactive Environmental Correlation Function</h3>
  <p>Adjust parameters to see how different environmental structures affect correlation functions:</p>
  <div id="correlation-function-plot" class="plot-container"></div>
  <!-- Controls added by JavaScript -->
</div>

### Open Quantum System Solvers

- Time-Convolutionless (TCL) master equations
- Non-Markovian Quantum Jump methods
- Numerically optimized for large parameter sweeps

<div class="collapsible-theory">
  <div class="collapsible-header">
    Mathematical Details: Time-Convolutionless Master Equation
    <span class="toggle-icon"><i class="fas fa-plus"></i></span>
  </div>
  <div class="collapsible-content">
    <p>The TCL master equation provides a systematic approach to non-Markovian dynamics by expanding the evolution generator to second order:</p>
    
    $$\frac{d\rho_S(t)}{dt} = -i[H_S, \rho_S(t)] + \mathcal{D}[\rho_S(t)]$$
    
    <p>Where the dissipator $\mathcal{D}$ is given by:</p>
    
    $$\mathcal{D}[\rho_S(t)] = \int_0^t d\tau \langle \mathcal{L}_{int}(t)\mathcal{L}_{int}(t-\tau)\rangle_E \rho_S(t)$$
    
    <p>This approach captures memory effects while maintaining computational tractability.</p>
  </div>
</div>

### Quantum Correlation Analysis

- Entanglement metrics (concurrence, negativity)
- Quantum discord calculations with numerical optimization
- Fisher information flow tracking

<div class="collapsible-theory">
  <div class="collapsible-header">
    Mathematical Details: Quantum Discord Calculation
    <span class="toggle-icon"><i class="fas fa-plus"></i></span>
  </div>
  <div class="collapsible-content">
    <p>Quantum discord quantifies non-classical correlations beyond entanglement:</p>
    
    $$D(A:B) = I(A:B) - J(A:B)$$
    
    <p>Where $I(A:B)$ is the mutual information:</p>
    
    $$I(A:B) = S(\rho_A) + S(\rho_B) - S(\rho_{AB})$$
    
    <p>And $J(A:B)$ is the classical correlation, computed via optimization over all possible measurements on $B$:</p>
    
    $$J(A:B) = S(\rho_A) - \min_{\{\Pi_j^B\}} \sum_j p_j S(\rho_{A|j})$$
    
    <p>Our implementation uses numerical optimization to find this minimum efficiently.</p>
  </div>
</div>

## Parameter Optimization

The framework enables:

- Systematic identification of optimal enhancement parameters
- Prediction of experimental conditions for maximal effect
- Visualization of enhancement regions in parameter space

<div class="visualization-container">
  <h3>Interactive Enhancement Factor</h3>
  <p>Explore how correlation enhancement depends on coupling strength:</p>
  <div id="enhancement-factor-plot" class="plot-container"></div>
  <!-- Controls added by JavaScript -->
</div>

## Example Results

Our simulations demonstrate:

- Non-monotonic dependence on coupling strength
- Optimal environmental correlation times
- Enhancement factors exceeding traditional bounds
- System-specific parameter optimization

These computational tools provide testable predictions for experimental validation while also allowing exploration of parameter regimes that may be challenging to access experimentally.

<div class="poll-container">
  <h3><i class="fas fa-poll"></i> Which correlation function should we simulate next?</h3>
  <p>Help us prioritize our next simulation targets:</p>
  <form id="correlation-poll-form">
    <div class="poll-options">
      <div class="poll-option">
        <input type="radio" id="option-1" name="correlation-type" value="Sub-Ohmic">
        <label for="option-1">Sub-Ohmic spectral density (1/f noise)</label>
      </div>
      <div class="poll-option">
        <input type="radio" id="option-2" name="correlation-type" value="Lorentzian">
        <label for="option-2">Lorentzian spectral density (cavity QED)</label>
      </div>
      <div class="poll-option">
        <input type="radio" id="option-3" name="correlation-type" value="Neural">
        <label for="option-3">Neural network oscillation patterns</label>
      </div>
      <div class="poll-option">
        <input type="radio" id="option-4" name="correlation-type" value="Custom">
        <label for="option-4">Custom user-defined correlation function</label>
      </div>
    </div>
    <button type="submit" class="poll-submit">Submit Vote</button>
  </form>
</div>

[View Example Code](../simulations/core/multi_scale_simulation.py)
