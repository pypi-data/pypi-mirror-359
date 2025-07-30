#!/usr/bin/env python3
"""
Comprehensive Analysis Script for Environmental Quantum Field Effects

This script performs end-to-end analysis of experimental data, from raw measurements
to final statistical validation and physics compliance checking.

Usage:
    python analyze_experimental_data.py [options]

Options:
    --data-file PATH        Path to experimental data file
    --output-dir PATH       Output directory for results
    --config-file PATH      Analysis configuration file
    --validation-level STR  Validation strictness (basic/standard/strict)
    --generate-plots        Generate analysis plots
    --export-results        Export results to multiple formats
"""

import argparse
import json
import os
import sys
from pathlib import Path
import warnings
from datetime import datetime
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Add package path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from simulations.core.field_simulator import EnvironmentalFieldSimulator
    from simulations.core.quantum_correlations import CHSHExperimentSimulator
    from simulations.analysis.physics_validator import (
        QuantumBoundsValidator,
        ValidationResult,
        validate_simulation_results,
        log_validation_results,
    )
    from simulations.analysis.experimental_analysis import (
        CHSHAnalyzer,
        EnvironmentalCorrelationAnalyzer,
        StatisticalValidator,
        ExperimentalData,
        comprehensive_analysis,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "Please ensure the package is properly installed or run from the correct directory"
    )
    sys.exit(1)


class ExperimentalDataLoader:
    """Load and validate experimental data from various formats."""

    def __init__(self):
        self.supported_formats = [".csv", ".json", ".hdf5", ".npz"]

    def load_data(self, file_path: str) -> ExperimentalData:
        """
        Load experimental data from file.

        Parameters:
        -----------
        file_path : str
            Path to data file

        Returns:
        --------
        ExperimentalData : Loaded experimental data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return self._load_csv(file_path)
        elif suffix == ".json":
            return self._load_json(file_path)
        elif suffix == ".hdf5":
            return self._load_hdf5(file_path)
        elif suffix == ".npz":
            return self._load_npz(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def _load_csv(self, file_path: Path) -> ExperimentalData:
        """Load data from CSV file."""
        df = pd.read_csv(file_path)

        # Expected columns
        required_cols = ["timestamp", "chsh_value"]
        optional_cols = ["magnetic_field", "electric_field", "temperature"]

        # Validate required columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Extract data
        timestamps = df["timestamp"].values
        chsh_values = df["chsh_value"].values

        # Environmental fields
        env_fields = {}
        for col in optional_cols:
            if col in df.columns:
                env_fields[col] = df[col].values

        # Correlations (if available)
        correlations = {}
        corr_cols = [col for col in df.columns if col.startswith("E_")]
        for col in corr_cols:
            correlations[col] = df[col].values

        # Detector counts (if available)
        detector_counts = {}
        count_cols = [col for col in df.columns if col.startswith("count_")]
        for col in count_cols:
            detector_counts[col] = df[col].values

        return ExperimentalData(
            timestamps=timestamps,
            chsh_values=chsh_values,
            correlations=correlations,
            environmental_fields=env_fields,
            detector_counts=detector_counts,
            analyzer_settings={},
            metadata={"source_file": str(file_path), "format": "csv"},
        )

    def _load_json(self, file_path: Path) -> ExperimentalData:
        """Load data from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        # Convert lists to numpy arrays
        timestamps = np.array(data["timestamps"])
        chsh_values = np.array(data["chsh_values"])

        correlations = {
            k: np.array(v) for k, v in data.get("correlations", {}).items()
        }
        env_fields = {
            k: np.array(v)
            for k, v in data.get("environmental_fields", {}).items()
        }
        detector_counts = {
            k: np.array(v) for k, v in data.get("detector_counts", {}).items()
        }
        analyzer_settings = {
            k: np.array(v)
            for k, v in data.get("analyzer_settings", {}).items()
        }

        return ExperimentalData(
            timestamps=timestamps,
            chsh_values=chsh_values,
            correlations=correlations,
            environmental_fields=env_fields,
            detector_counts=detector_counts,
            analyzer_settings=analyzer_settings,
            metadata=data.get("metadata", {}),
        )

    def _load_npz(self, file_path: Path) -> ExperimentalData:
        """Load data from NumPy compressed file."""
        data = np.load(file_path, allow_pickle=True)

        timestamps = data["timestamps"]
        chsh_values = data["chsh_values"]

        # Handle optional arrays
        correlations = (
            data.get("correlations", {}).item()
            if "correlations" in data
            else {}
        )
        env_fields = (
            data.get("environmental_fields", {}).item()
            if "environmental_fields" in data
            else {}
        )
        detector_counts = (
            data.get("detector_counts", {}).item()
            if "detector_counts" in data
            else {}
        )
        analyzer_settings = (
            data.get("analyzer_settings", {}).item()
            if "analyzer_settings" in data
            else {}
        )
        metadata = (
            data.get("metadata", {}).item() if "metadata" in data else {}
        )

        return ExperimentalData(
            timestamps=timestamps,
            chsh_values=chsh_values,
            correlations=correlations,
            environmental_fields=env_fields,
            detector_counts=detector_counts,
            analyzer_settings=analyzer_settings,
            metadata=metadata,
        )


class AnalysisReportGenerator:
    """Generate comprehensive analysis reports."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set plotting style
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

    def generate_report(
        self, data: ExperimentalData, results: Any, config: Dict
    ) -> str:
        """
        Generate comprehensive analysis report.

        Parameters:
        -----------
        data : ExperimentalData
            Original experimental data
        results : AnalysisResults
            Analysis results
        config : dict
            Analysis configuration

        Returns:
        --------
        str : Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.output_dir / f"analysis_report_{timestamp}"
        report_dir.mkdir(exist_ok=True)

        # Generate plots
        plot_files = self._generate_plots(data, results, report_dir)

        # Generate statistical summary
        stats_file = self._generate_statistics_summary(results, report_dir)

        # Generate physics validation report
        validation_file = self._generate_validation_report(results, report_dir)

        # Generate main HTML report
        html_file = self._generate_html_report(
            data,
            results,
            config,
            plot_files,
            stats_file,
            validation_file,
            report_dir,
        )

        # Export data
        self._export_results(data, results, report_dir)

        return str(html_file)

    def _generate_plots(
        self, data: ExperimentalData, results: Any, output_dir: Path
    ) -> Dict[str, str]:
        """Generate analysis plots."""
        plot_files = {}

        # Time series plot
        plt.figure(figsize=(12, 8))

        plt.subplot(3, 1, 1)
        plt.plot(
            data.timestamps,
            data.chsh_values,
            "b-",
            alpha=0.7,
            label="CHSH Parameter",
        )
        plt.axhline(y=2.0, color="r", linestyle="--", label="Classical Bound")
        plt.axhline(
            y=2 * np.sqrt(2),
            color="g",
            linestyle="--",
            label="Tsirelson Bound",
        )
        plt.ylabel("CHSH Parameter S")
        plt.legend()
        plt.title("CHSH Parameter Time Evolution")

        # Environmental field
        if "magnetic_field" in data.environmental_fields:
            plt.subplot(3, 1, 2)
            field_data = data.environmental_fields["magnetic_field"]
            plt.plot(data.timestamps, field_data, "orange", alpha=0.7)
            plt.ylabel("Magnetic Field (nT)")
            plt.title("Environmental Magnetic Field")

        # Field variance
        if hasattr(results, "field_variance"):
            plt.subplot(3, 1, 3)
            plt.plot(
                data.timestamps, results.field_variance, "purple", alpha=0.7
            )
            plt.ylabel("Field Variance")
            plt.xlabel("Time (s)")
            plt.title("Environmental Field Variance")

        plt.tight_layout()
        timeseries_file = output_dir / "timeseries_analysis.png"
        plt.savefig(timeseries_file, dpi=300, bbox_inches="tight")
        plt.close()
        plot_files["timeseries"] = str(timeseries_file)

        # Correlation analysis plot
        plt.figure(figsize=(10, 6))

        if "magnetic_field" in data.environmental_fields:
            field_data = data.environmental_fields["magnetic_field"]
            field_variance = np.var(field_data) * np.ones_like(
                data.chsh_values
            )  # Simplified

            plt.scatter(field_variance, data.chsh_values, alpha=0.6, s=20)

            # Fit line
            z = np.polyfit(field_variance, data.chsh_values, 1)
            p = np.poly1d(z)
            plt.plot(
                field_variance,
                p(field_variance),
                "r--",
                alpha=0.8,
                linewidth=2,
            )

            # Correlation coefficient
            corr_coef = np.corrcoef(field_variance, data.chsh_values)[0, 1]
            plt.text(
                0.05,
                0.95,
                f"r = {corr_coef:.3f}",
                transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

        plt.xlabel("Environmental Field Variance")
        plt.ylabel("CHSH Parameter S")
        plt.title("CHSH vs Environmental Field Correlation")

        correlation_file = output_dir / "correlation_analysis.png"
        plt.savefig(correlation_file, dpi=300, bbox_inches="tight")
        plt.close()
        plot_files["correlation"] = str(correlation_file)

        # Distribution analysis
        plt.figure(figsize=(12, 4))

        plt.subplot(1, 3, 1)
        plt.hist(
            data.chsh_values,
            bins=50,
            alpha=0.7,
            density=True,
            edgecolor="black",
        )
        plt.axvline(x=2.0, color="r", linestyle="--", label="Classical")
        plt.axvline(
            x=2 * np.sqrt(2), color="g", linestyle="--", label="Tsirelson"
        )
        plt.xlabel("CHSH Parameter S")
        plt.ylabel("Probability Density")
        plt.title("CHSH Distribution")
        plt.legend()

        plt.subplot(1, 3, 2)
        if "magnetic_field" in data.environmental_fields:
            field_data = data.environmental_fields["magnetic_field"]
            plt.hist(
                field_data,
                bins=50,
                alpha=0.7,
                density=True,
                edgecolor="black",
                color="orange",
            )
            plt.xlabel("Magnetic Field (nT)")
            plt.ylabel("Probability Density")
            plt.title("Field Distribution")

        plt.subplot(1, 3, 3)
        stats.probplot(data.chsh_values, dist="norm", plot=plt)
        plt.title("CHSH Normal Q-Q Plot")

        plt.tight_layout()
        distribution_file = output_dir / "distribution_analysis.png"
        plt.savefig(distribution_file, dpi=300, bbox_inches="tight")
        plt.close()
        plot_files["distribution"] = str(distribution_file)

        return plot_files

    def _generate_statistics_summary(
        self, results: Any, output_dir: Path
    ) -> str:
        """Generate statistical summary."""
        stats_file = output_dir / "statistical_summary.txt"

        with open(stats_file, "w") as f:
            f.write(
                "ENVIRONMENTAL QUANTUM FIELD EFFECTS - STATISTICAL SUMMARY\n"
            )
            f.write("=" * 60 + "\n\n")

            # Basic statistics
            if hasattr(results, "statistical_tests"):
                bell_test = results.statistical_tests.get("bell_test", {})
                f.write("Bell Inequality Analysis:\n")
                f.write(
                    f"  Mean CHSH Parameter: {bell_test.get('mean_chsh', 'N/A'):.4f}\n"
                )
                f.write(
                    f"  Standard Deviation: {bell_test.get('std_chsh', 'N/A'):.4f}\n"
                )
                f.write(
                    f"  Classical Violations: {bell_test.get('classical_violations', 'N/A')}\n"
                )
                f.write(
                    f"  Tsirelson Violations: {bell_test.get('tsirelson_violations', 'N/A')}\n"
                )
                f.write(
                    f"  Classical p-value: {bell_test.get('classical_p_value', 'N/A'):.2e}\n"
                )
                f.write(
                    f"  Tsirelson p-value: {bell_test.get('tsirelson_p_value', 'N/A'):.2e}\n\n"
                )

            # Correlation analysis
            if hasattr(results, "correlation_coefficients"):
                f.write("Environmental Correlation Analysis:\n")
                for key, value in results.correlation_coefficients.items():
                    f.write(f"  {key}: {value:.4f}\n")
                f.write("\n")

            # Amplification parameters
            if hasattr(results, "amplification_params"):
                f.write("Amplification Law Parameters:\n")
                for key, value in results.amplification_params.items():
                    if isinstance(value, (int, float)):
                        f.write(f"  {key}: {value:.6e}\n")
                f.write("\n")

            # Fit quality
            if hasattr(results, "fit_quality"):
                f.write("Model Fit Quality:\n")
                for key, value in results.fit_quality.items():
                    f.write(f"  {key}: {value:.4f}\n")

        return str(stats_file)

    def _generate_validation_report(
        self, results: Any, output_dir: Path
    ) -> str:
        """Generate physics validation report."""
        validation_file = output_dir / "physics_validation.txt"

        with open(validation_file, "w") as f:
            f.write("PHYSICS VALIDATION REPORT\n")
            f.write("=" * 30 + "\n\n")

            if hasattr(results, "validation_results"):
                validation = results.validation_results

                f.write(
                    f"Overall Validation: {'PASSED' if validation.is_valid else 'FAILED'}\n\n"
                )

                if validation.violations:
                    f.write("VIOLATIONS DETECTED:\n")
                    for violation in validation.violations:
                        f.write(f"  ✗ {violation}\n")
                    f.write("\n")

                if validation.warnings:
                    f.write("WARNINGS:\n")
                    for warning in validation.warnings:
                        f.write(f"  ⚠ {warning}\n")
                    f.write("\n")

                f.write("BOUNDS CHECKED:\n")
                for check, passed in validation.bounds_checked.items():
                    status = "✓" if passed else "✗"
                    f.write(f"  {status} {check}\n")

        return str(validation_file)

    def _generate_html_report(
        self,
        data,
        results,
        config,
        plot_files,
        stats_file,
        validation_file,
        output_dir,
    ) -> str:
        """Generate main HTML report."""
        html_file = output_dir / "analysis_report.html"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Environmental Quantum Field Effects - Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #2c3e50; }}
                .section {{ margin: 30px 0; }}
                .plot {{ text-align: center; margin: 20px 0; }}
                .plot img {{ max-width: 100%; height: auto; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .validation-pass {{ color: #27ae60; }}
                .validation-fail {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Environmental Quantum Field Effects</h1>
                <h2>Experimental Data Analysis Report</h2>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h3>Data Summary</h3>
                <div class="summary">
                    <p><strong>Data Points:</strong> {len(data.timestamps)}</p>
                    <p><strong>Time Range:</strong> {data.timestamps[0]:.1f} - {data.timestamps[-1]:.1f} seconds</p>
                    <p><strong>Mean CHSH:</strong> {np.mean(data.chsh_values):.4f}</p>
                    <p><strong>CHSH Range:</strong> {np.min(data.chsh_values):.4f} - {np.max(data.chsh_values):.4f}</p>
                </div>
            </div>
            
            <div class="section">
                <h3>Physics Validation</h3>
                <div class="summary">
                    <p class="{'validation-pass' if results.validation_results.is_valid else 'validation-fail'}">
                        <strong>Status:</strong> {'PASSED' if results.validation_results.is_valid else 'FAILED'}
                    </p>
                    <p><a href="physics_validation.txt">Detailed Validation Report</a></p>
                </div>
            </div>
            
            <div class="section">
                <h3>Time Series Analysis</h3>
                <div class="plot">
                    <img src="{Path(plot_files['timeseries']).name}" alt="Time Series Analysis">
                </div>
            </div>
            
            <div class="section">
                <h3>Environmental Correlation</h3>
                <div class="plot">
                    <img src="{Path(plot_files['correlation']).name}" alt="Correlation Analysis">
                </div>
            </div>
            
            <div class="section">
                <h3>Statistical Distributions</h3>
                <div class="plot">
                    <img src="{Path(plot_files['distribution']).name}" alt="Distribution Analysis">
                </div>
            </div>
            
            <div class="section">
                <h3>Additional Resources</h3>
                <ul>
                    <li><a href="statistical_summary.txt">Statistical Summary</a></li>
                    <li><a href="results_data.json">Raw Results (JSON)</a></li>
                    <li><a href="results_data.npz">Raw Results (NumPy)</a></li>
                </ul>
            </div>
        </body>
        </html>
        """

        with open(html_file, "w") as f:
            f.write(html_content)

        return str(html_file)

    def _export_results(
        self, data: ExperimentalData, results: Any, output_dir: Path
    ):
        """Export results in multiple formats."""
        # JSON export
        results_dict = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "data_points": len(data.timestamps),
                "time_range": [
                    float(data.timestamps[0]),
                    float(data.timestamps[-1]),
                ],
            },
            "chsh_statistics": {
                "mean": float(np.mean(data.chsh_values)),
                "std": float(np.std(data.chsh_values)),
                "min": float(np.min(data.chsh_values)),
                "max": float(np.max(data.chsh_values)),
            },
        }

        # Add results if available
        if hasattr(results, "correlation_coefficients"):
            results_dict["correlations"] = results.correlation_coefficients

        if hasattr(results, "amplification_params"):
            # Convert numpy types to Python types for JSON serialization
            amp_params = {}
            for k, v in results.amplification_params.items():
                if isinstance(v, (np.integer, np.floating)):
                    amp_params[k] = float(v)
                elif isinstance(v, bool):
                    amp_params[k] = bool(v)
                else:
                    amp_params[k] = v
            results_dict["amplification_parameters"] = amp_params

        json_file = output_dir / "results_data.json"
        with open(json_file, "w") as f:
            json.dump(results_dict, f, indent=2)

        # NumPy export
        npz_data = {
            "timestamps": data.timestamps,
            "chsh_values": data.chsh_values,
            "metadata": results_dict["metadata"],
        }

        if data.environmental_fields:
            npz_data["environmental_fields"] = data.environmental_fields

        npz_file = output_dir / "results_data.npz"
        np.savez_compressed(npz_file, **npz_data)


def create_analysis_config() -> Dict[str, Any]:
    """Create default analysis configuration."""
    return {
        "validation": {
            "level": "standard",
            "tsirelson_tolerance": 1e-10,
            "require_quantum_advantage": True,
        },
        "correlation_analysis": {
            "methods": ["pearson", "spearman"],
            "significance_level": 0.001,
            "max_lag": 100,
        },
        "amplification_fitting": {
            "enable": True,
            "max_iterations": 5000,
            "parameter_bounds": {
                "alpha": [0, 1.0],
                "beta": [0, 1.0],
                "tau_c": [0, 1000],
            },
        },
        "plotting": {
            "generate_plots": True,
            "plot_format": "png",
            "plot_dpi": 300,
        },
    }


def main():
    """Main analysis function."""
    parser = argparse.ArgumentParser(
        description="Analyze Environmental Quantum Field Effects experimental data"
    )

    parser.add_argument(
        "--data-file", required=True, help="Path to experimental data file"
    )
    parser.add_argument(
        "--output-dir",
        default="./analysis_results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--config-file", help="Analysis configuration file (JSON)"
    )
    parser.add_argument(
        "--validation-level",
        default="standard",
        choices=["basic", "standard", "strict"],
        help="Physics validation strictness level",
    )
    parser.add_argument(
        "--generate-plots", action="store_true", help="Generate analysis plots"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    else:
        logger = None

    try:
        # Load configuration
        if args.config_file:
            with open(args.config_file, "r") as f:
                config = json.load(f)
        else:
            config = create_analysis_config()

        # Override config with command line options
        config["validation"]["level"] = args.validation_level
        config["plotting"]["generate_plots"] = args.generate_plots

        print("Environmental Quantum Field Effects - Data Analysis")
        print("=" * 60)

        # Load experimental data
        print(f"Loading data from: {args.data_file}")
        loader = ExperimentalDataLoader()
        data = loader.load_data(args.data_file)

        print(f"Loaded {len(data.timestamps)} data points")
        print(
            f"Time range: {data.timestamps[0]:.1f} - {data.timestamps[-1]:.1f} seconds"
        )
        print(
            f"CHSH range: {np.min(data.chsh_values):.4f} - {np.max(data.chsh_values):.4f}"
        )

        # Perform comprehensive analysis
        print("\nPerforming comprehensive analysis...")
        results = comprehensive_analysis(data)

        # Log validation results
        print("\nPhysics Validation Results:")
        log_validation_results(results.validation_results, logger)

        # Generate report
        print(f"\nGenerating analysis report in: {args.output_dir}")
        report_generator = AnalysisReportGenerator(args.output_dir)
        report_path = report_generator.generate_report(data, results, config)

        print(f"\nAnalysis complete!")
        print(f"Report generated: {report_path}")

        # Summary statistics
        print("\nSummary Statistics:")
        print(f"  Mean CHSH: {np.mean(data.chsh_values):.4f}")
        print(
            f"  Classical violations: {np.sum(data.chsh_values > 2.0)}/{len(data.chsh_values)}"
        )
        print(
            f"  Tsirelson violations: {np.sum(data.chsh_values > 2*np.sqrt(2))}/{len(data.chsh_values)}"
        )

        if hasattr(results, "correlation_coefficients"):
            for key, value in results.correlation_coefficients.items():
                print(f"  {key}: {value:.4f}")

        return 0

    except Exception as e:
        print(f"Analysis failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
