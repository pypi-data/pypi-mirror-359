"""
Example usage of the EQFE Hardware Abstraction Layer.

This script demonstrates how to use the unified hardware manager
to run quantum field experiments.
"""

import logging
import time
from hardware import HardwareManager, ExperimentConfig, ExperimentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main example function."""
    logger = logging.getLogger("EQFE.example")
    
    # Hardware configuration
    hardware_config = {
        'quantum_sensors': {
            'photon_detector_1': {
                'type': 'single_photon_detector',
                'efficiency': 0.85,
                'dark_count_rate': 100,
                'timing_resolution': 50e-12
            },
            'interferometer_1': {
                'type': 'interferometer',
                'visibility': 0.95,
                'phase_stability': 0.01,
                'wavelength': 780e-9
            }
        },
        'field_generators': {
            'em_field_1': {
                'type': 'electromagnetic',
                'frequency_range': [1e3, 1e9],
                'max_field_strength': 1e-3
            },
            'temp_controller_1': {
                'type': 'temperature',
                'temperature_range': [4.0, 400.0],
                'stability': 0.01
            }
        },
        'data_acquisition': {
            'digitizer_1': {
                'type': 'high_speed_digitizer',
                'sample_rate': 1e9,
                'resolution': 14,
                'num_channels': 4
            }
        },
        'drivers': {
            'scope_1': {
                'type': 'oscilloscope',
                'address': 'TCPIP::192.168.1.100::INSTR',
                'bandwidth': 1e9,
                'max_sample_rate': 5e9
            },
            'signal_gen_1': {
                'type': 'signal_generator', 
                'address': 'TCPIP::192.168.1.101::INSTR',
                'frequency_range': [1e3, 6e9]
            }
        }
    }
    
    # Initialize hardware manager
    logger.info("Initializing hardware manager...")
    hw_manager = HardwareManager(hardware_config)
    
    try:
        # Initialize all hardware
        if not hw_manager.initialize_hardware():
            logger.error("Hardware initialization failed")
            return
            
        logger.info("Hardware initialization successful")
        
        # Get system status
        status = hw_manager.get_system_status()
        logger.info(f"System state: {status['state']}")
        logger.info(f"System health: {status['system_health']}")
        
        # Configure experiment
        experiment_config = ExperimentConfig(
            measurement_duration=30.0,  # 30 seconds
            sample_rate=1e6,
            target_temperature=300.0,  # Room temperature
            field_frequency=1e6,  # 1 MHz
            field_amplitude=1e-6,  # 1 μT
            channels_to_record=[1, 2],
            trigger_level=0.1,
            auto_calibrate=True
        )
        
        logger.info("Starting EQFE experiment...")
        
        # Run experiment
        success = hw_manager.run_experiment(experiment_config)
        
        if success:
            logger.info("Experiment completed successfully!")
            
            # Get final system status
            final_status = hw_manager.get_system_status()
            logger.info(f"Final system state: {final_status['state']}")
            
            # Display measurement summary
            if hw_manager.measurement_data:
                logger.info("Measurement data collected:")
                for daq_id, data in hw_manager.measurement_data.items():
                    logger.info(f"  {daq_id}: {len(data)} data points")
        else:
            logger.error("Experiment failed!")
            
    except KeyboardInterrupt:
        logger.info("Experiment interrupted by user")
        
    finally:
        # Safely shutdown hardware
        logger.info("Shutting down hardware...")
        hw_manager.shutdown_hardware()
        logger.info("Hardware shutdown complete")


def demonstrate_individual_components():
    """Demonstrate individual hardware components."""
    logger = logging.getLogger("EQFE.demo")
    
    # Example of using individual hardware interfaces
    logger.info("Demonstrating individual hardware interfaces...")
    
    # Quantum sensor simulation
    from hardware.interfaces.quantum_sensors import SinglePhotonDetector
    
    detector_config = {
        'efficiency': 0.85,
        'dark_count_rate': 100,
        'timing_resolution': 50e-12
    }
    
    detector = SinglePhotonDetector("demo_detector", detector_config)
    
    if detector.connect():
        logger.info("Connected to photon detector")
        
        # Simulate measurement
        correlations = detector.measure_correlations(duration=1.0)
        logger.info(f"Measured {correlations['detection_events']} photon events")
        
        # Get detector status
        status = detector.get_status()
        logger.info(f"Detector temperature: {status['temperature']:.1f}°C")
        
        detector.disconnect()
    else:
        logger.error("Failed to connect to detector")
        
    # Field generator simulation
    from hardware.interfaces.field_generators import ElectromagneticFieldGenerator
    
    field_config = {
        'frequency_range': [1e3, 1e9],
        'max_field_strength': 1e-3
    }
    
    field_gen = ElectromagneticFieldGenerator("demo_field", field_config)
    
    if field_gen.connect():
        logger.info("Connected to field generator")
        
        # Set field parameters
        field_params = {
            'frequency': 1e6,  # 1 MHz
            'amplitude': 1e-6  # 1 μT
        }
        
        if field_gen.set_field_parameters(field_params):
            logger.info("Field parameters set successfully")
            
            # Start field generation
            if field_gen.start_field_generation():
                logger.info("Field generation started")
                time.sleep(2)  # Generate field for 2 seconds
                
                # Get field status
                status = field_gen.get_field_status()
                logger.info(f"Field active: {status['active']}")
                logger.info(f"Field frequency: {status['frequency']:.2e} Hz")
                
                field_gen.stop_field_generation()
                logger.info("Field generation stopped")
                
        field_gen.disconnect()
    else:
        logger.error("Failed to connect to field generator")


if __name__ == "__main__":
    print("EQFE Hardware Abstraction Layer Example")
    print("=" * 40)
    
    # Run main example
    main()
    
    print("\n" + "=" * 40)
    print("Individual Component Demonstration")
    print("=" * 40)
    
    # Demonstrate individual components
    demonstrate_individual_components()
    
    print("\nExample complete!")
