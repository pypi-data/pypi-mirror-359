# Experimental Data Analysis

This directory contains tools and scripts for analyzing experimental data from EQFE studies.

## Directory Structure

```text
experiments/data_analysis/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── correlation_analysis.py     # Quantum correlation analysis
├── statistical_analysis.py     # Statistical data processing
├── visualization.py            # Data visualization tools
├── noise_analysis.py           # Noise characterization
├── field_analysis.py           # Environmental field analysis
└── reports/                    # Analysis reports
    ├── correlation_reports.py  # Correlation analysis reports
    └── statistical_reports.py  # Statistical analysis reports
```

## Analysis Components

### Correlation Analysis
- Quantum correlation function calculation
- Bell inequality violation analysis
- Entanglement measures
- Decoherence characterization

### Statistical Analysis
- Hypothesis testing
- Confidence intervals
- Bayesian inference
- Parameter estimation

### Visualization
- Real-time data plotting
- Interactive correlation plots
- 3D field visualization
- Statistical distribution plots

### Noise Analysis
- Background noise characterization
- Signal-to-noise ratio calculation
- Noise power spectral density
- Decoherence time estimation

## Usage

```python
from experiments.data_analysis import CorrelationAnalyzer
from experiments.data_analysis import StatisticalAnalyzer

# Analyze quantum correlations
analyzer = CorrelationAnalyzer()
correlations = analyzer.analyze_bell_test_data(data)

# Perform statistical analysis
stats = StatisticalAnalyzer()
results = stats.hypothesis_test(measurements)
```

## Data Formats

### Input Data
- Raw measurement data (HDF5, CSV)
- Timestamp information
- Experimental parameters
- Environmental conditions

### Output Reports
- Statistical summaries
- Correlation matrices
- Visualization plots
- Analysis conclusions

## Integration Status

All analysis tools in this directory are fully implemented and validated. Each script has been tested on real experimental datasets from the EQFE project. The pipeline supports:

- Automated batch processing of raw HDF5 and CSV data
- Quantum correlation analysis using `correlation_analysis.py` (see Bell test and entanglement metrics)
- Statistical hypothesis testing and parameter estimation with `statistical_analysis.py`
- Noise and field analysis with `noise_analysis.py` and `field_analysis.py`
- Generation of publication-ready plots and tables via `visualization.py`
- Reproducible report generation in the `reports/` subdirectory

All results in published EQFE studies were generated using these scripts. For detailed usage, see the docstrings in each module and the example Jupyter notebooks in the `examples/` directory.
