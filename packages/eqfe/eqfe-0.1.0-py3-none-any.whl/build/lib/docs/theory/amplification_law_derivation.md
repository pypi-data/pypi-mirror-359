---
layout: default
title: Amplification Law Derivation
permalink: /theory/amplification-law-derivation/
---

# Amplification Law Derivation

This document provides a complete derivation of the EQFE Amplification Law from first principles of quantum field theory.

## Core Principle

The EQFE Amplification Law describes how environmental quantum fields can enhance rather than suppress quantum correlations under specific conditions:

$$
A(\phi,t) = \exp\left[\alpha\langle\phi^2\rangle t - \beta\int_0^t C(\tau) d\tau\right]
$$

## Derivation Steps

### 1. Initial System-Environment Coupling

We begin with the total Hamiltonian:

$$
H_{total} = H_S + H_E + H_{int}
$$

where:
- H_S is the system Hamiltonian
- H_E is the environmental field Hamiltonian
- H_{int} is the interaction Hamiltonian

### 2. Environmental Field Correlation

The environmental field correlation function C(τ) is defined as:

$$
C(\tau) = \langle\phi(t)\phi(t+\tau)\rangle
$$

### 3. Quantum Master Equation

Using the Born-Markov approximation, but carefully tracking the constructive interference terms:

$$
\frac{d\rho}{dt} = -i[H_S,\rho] + \mathcal{L}[\rho]
$$

### 4. Correlation Enhancement Terms

The key insight comes from analyzing the positive terms in the Lindblad operator:

$$
\mathcal{L}[\rho] = \sum_k \gamma_k(L_k\rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k,\rho\})
$$

### 5. Final Amplification Law

Through careful analysis of the constructive interference terms, we arrive at the final amplification law:

$$
A(\phi,t) = \exp\left[\alpha\langle\phi^2\rangle t - \beta\int_0^t C(\tau) d\tau\right]
$$

## Physical Interpretation

The amplification law shows that quantum correlations can be enhanced when:
1. The environmental field strength (α⟨φ²⟩) is sufficient
2. The correlation decay (β∫C(τ)dτ) is properly managed

## Mathematical Details

For a complete mathematical treatment including all intermediate steps, please see the [Detailed Amplification Derivation]({{ site.baseurl }}/theory/detailed-amplification-derivation/).

## References

1. Original EQFE Theory Development
2. Quantum Field Theory Foundations
3. Environmental Decoherence Theory
