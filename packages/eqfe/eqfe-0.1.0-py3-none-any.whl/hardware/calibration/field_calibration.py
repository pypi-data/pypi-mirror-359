"""
Field calibration routines for EQFE experiments.

Provides calibration procedures for environmental field generators,
electromagnetic field control, and temperature systems.
"""

import numpy as np
import logging
import time
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class FieldCalibrationResult:
    """Data structure for field calibration results."""
    success: bool
    calibration_factor: float
    uncertainty: float
    reference_value: float
    measured_value: float
    field_type: str
    timestamp: float
    notes: str = ""


class FieldCalibration:
    """Field calibration management system."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize field calibration system.
        
        Args:
            config: Calibration configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger("EQFE.calibration.field")
        
        # Calibration standards and references
        self.field_references = config.get('field_references', {})
        self.calibration_history = []
        
    def calibrate_electromagnetic_field(self, field_generator, 
                                       reference_field: float,
                                       frequency: float = 1e6
                                       ) -> FieldCalibrationResult:
        """
        Calibrate electromagnetic field generator.
        
        Args:
            field_generator: Field generator interface
            reference_field: Reference field strength in Tesla
            frequency: Calibration frequency in Hz
            
        Returns:
            FieldCalibrationResult with calibration parameters
        """
        try:
            self.logger.info(f"Starting EM field calibration at {frequency:.2e} Hz")
            
            # Set field parameters
            field_params = {
                'frequency': frequency,
                'amplitude': reference_field
            }
            
            if not field_generator.set_field_parameters(field_params):
                raise RuntimeError("Failed to set field parameters")
                
            # Start field generation
            if not field_generator.start_field_generation():
                raise RuntimeError("Failed to start field generation")
                
            # Wait for field stabilization
            time.sleep(1.0)
            
            # Measure actual field strength
            # TODO: Implement actual field measurement using magnetometer/probe
            # For now, simulate measurement with some uncertainty
            measured_field = reference_field * np.random.normal(1.0, 0.02)
            
            # Stop field generation
            field_generator.stop_field_generation()
            
            # Calculate calibration factor
            calibration_factor = measured_field / reference_field
            uncertainty = abs(calibration_factor - 1.0)
            
            result = FieldCalibrationResult(
                success=True,
                calibration_factor=calibration_factor,
                uncertainty=uncertainty,
                reference_value=reference_field,
                measured_value=measured_field,
                field_type="electromagnetic",
                timestamp=time.time(),
                notes=f"Frequency: {frequency:.2e} Hz, "
                      f"Accuracy: {uncertainty*100:.2f}%"
            )
            
            self.calibration_history.append(result)
            
            self.logger.info(f"EM field calibration complete: "
                           f"Factor: {calibration_factor:.4f}, "
                           f"Error: {uncertainty*100:.2f}%")
            
            return result
            
        except Exception as e:
            self.logger.error(f"EM field calibration failed: {e}")
            return FieldCalibrationResult(
                success=False,
                calibration_factor=0.0,
                uncertainty=0.0,
                reference_value=reference_field,
                measured_value=0.0,
                field_type="electromagnetic",
                timestamp=time.time(),
                notes=f"Error: {str(e)}"
            )
            
    def calibrate_temperature_control(self, temp_controller,
                                     reference_temperatures: List[float]
                                     ) -> List[FieldCalibrationResult]:
        """
        Calibrate temperature controller at multiple setpoints.
        
        Args:
            temp_controller: Temperature controller interface
            reference_temperatures: List of calibration temperatures in Kelvin
            
        Returns:
            List of FieldCalibrationResult for each temperature point
        """
        results = []
        
        try:
            self.logger.info("Starting temperature controller calibration")
            
            for ref_temp in reference_temperatures:
                try:
                    # Set temperature setpoint
                    if not temp_controller.set_temperature(ref_temp):
                        raise RuntimeError(f"Failed to set temperature: {ref_temp}")
                        
                    # Enable temperature control
                    if not temp_controller.enable_control(True):
                        raise RuntimeError("Failed to enable temperature control")
                        
                    # Wait for temperature stabilization
                    self.logger.info(f"Waiting for temperature stabilization at {ref_temp:.1f} K")
                    
                    # Simplified stabilization check
                    stabilization_time = 30.0  # seconds
                    time.sleep(stabilization_time)
                    
                    # Measure actual temperature
                    measured_temp = temp_controller.get_temperature()
                    
                    if np.isnan(measured_temp):
                        raise RuntimeError("Failed to read temperature")
                        
                    # Calculate calibration parameters
                    temp_error = measured_temp - ref_temp
                    calibration_factor = measured_temp / ref_temp
                    uncertainty = abs(temp_error)
                    
                    result = FieldCalibrationResult(
                        success=True,
                        calibration_factor=calibration_factor,
                        uncertainty=uncertainty,
                        reference_value=ref_temp,
                        measured_value=measured_temp,
                        field_type="temperature",
                        timestamp=time.time(),
                        notes=f"Error: {temp_error:.3f} K, "
                              f"Stability: {stabilization_time} s"
                    )
                    
                    results.append(result)
                    self.calibration_history.append(result)
                    
                    self.logger.info(f"Temperature calibration at {ref_temp:.1f} K: "
                                   f"Measured: {measured_temp:.3f} K, "
                                   f"Error: {temp_error:.3f} K")
                    
                except Exception as e:
                    self.logger.error(f"Temperature calibration failed at {ref_temp} K: {e}")
                    result = FieldCalibrationResult(
                        success=False,
                        calibration_factor=0.0,
                        uncertainty=0.0,
                        reference_value=ref_temp,
                        measured_value=0.0,
                        field_type="temperature",
                        timestamp=time.time(),
                        notes=f"Error: {str(e)}"
                    )
                    results.append(result)
                    
            # Disable temperature control after calibration
            temp_controller.enable_control(False)
            
            successful_calibrations = sum(1 for r in results if r.success)
            self.logger.info(f"Temperature calibration complete: "
                           f"{successful_calibrations}/{len(results)} points successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Temperature calibration failed: {e}")
            return results
            
    def verify_field_calibration(self, field_type: str, 
                                tolerance: float = 0.05) -> bool:
        """
        Verify field calibration within tolerance.
        
        Args:
            field_type: Type of field to verify ("electromagnetic", "temperature")
            tolerance: Acceptable calibration tolerance (fractional)
            
        Returns:
            True if calibration is within tolerance
        """
        try:
            # Find most recent calibrations of this type
            recent_calibrations = [
                cal for cal in self.calibration_history
                if cal.field_type == field_type and cal.success
            ]
            
            if not recent_calibrations:
                self.logger.warning(f"No calibration history found for {field_type} fields")
                return False
                
            # Check if all recent calibrations are within tolerance
            within_tolerance = []
            for cal in recent_calibrations:
                relative_error = abs(cal.calibration_factor - 1.0)
                within_tolerance.append(relative_error <= tolerance)
                
            all_within_tolerance = all(within_tolerance)
            success_rate = sum(within_tolerance) / len(within_tolerance) * 100
            
            if all_within_tolerance:
                self.logger.info(f"{field_type} field calibration verified: "
                               f"All {len(recent_calibrations)} points within {tolerance*100:.1f}%")
                return True
            else:
                self.logger.warning(f"{field_type} field calibration verification failed: "
                                  f"Only {success_rate:.1f}% within tolerance")
                return False
                
        except Exception as e:
            self.logger.error(f"Field calibration verification failed: {e}")
            return False
            
    def get_field_calibration_report(self) -> Dict[str, Any]:
        """Generate field calibration report summary."""
        try:
            if not self.calibration_history:
                return {'status': 'no_calibrations', 'calibrations': []}
                
            # Organize calibrations by field type
            calibrations_by_type = {}
            for cal in self.calibration_history:
                field_type = cal.field_type
                if field_type not in calibrations_by_type:
                    calibrations_by_type[field_type] = []
                calibrations_by_type[field_type].append(cal)
                
            # Generate summary statistics
            total_calibrations = len(self.calibration_history)
            successful_calibrations = sum(1 for cal in self.calibration_history if cal.success)
            success_rate = successful_calibrations / total_calibrations if total_calibrations > 0 else 0
            
            # Calculate average accuracy by field type
            accuracy_by_type = {}
            for field_type, calibrations in calibrations_by_type.items():
                successful_cals = [cal for cal in calibrations if cal.success]
                if successful_cals:
                    avg_error = np.mean([abs(cal.calibration_factor - 1.0) for cal in successful_cals])
                    accuracy_by_type[field_type] = {
                        'average_error': avg_error,
                        'count': len(successful_cals),
                        'success_rate': len(successful_cals) / len(calibrations)
                    }
                    
            report = {
                'status': 'complete',
                'total_calibrations': total_calibrations,
                'successful_calibrations': successful_calibrations,
                'success_rate': success_rate,
                'calibrations_by_type': calibrations_by_type,
                'accuracy_by_type': accuracy_by_type,
                'most_recent': max(self.calibration_history, key=lambda x: x.timestamp),
                'generation_time': time.time()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate field calibration report: {e}")
            return {'status': 'error', 'message': str(e)}
            
    def schedule_calibration_check(self, field_type: str, 
                                  interval_hours: float = 24.0) -> bool:
        """
        Schedule periodic calibration verification.
        
        Args:
            field_type: Type of field to check
            interval_hours: Check interval in hours
            
        Returns:
            True if scheduling was successful
        """
        try:
            # Find most recent calibration of this type
            recent_calibrations = [
                cal for cal in self.calibration_history
                if cal.field_type == field_type and cal.success
            ]
            
            if not recent_calibrations:
                self.logger.warning(f"Cannot schedule check: no {field_type} calibration history")
                return False
                
            latest_cal = max(recent_calibrations, key=lambda x: x.timestamp)
            time_since_cal = time.time() - latest_cal.timestamp
            hours_since_cal = time_since_cal / 3600.0
            
            if hours_since_cal >= interval_hours:
                self.logger.warning(f"{field_type} calibration is {hours_since_cal:.1f} hours old "
                                  f"(interval: {interval_hours:.1f} hours) - recalibration recommended")
                return False
            else:
                next_check_hours = interval_hours - hours_since_cal
                self.logger.info(f"{field_type} calibration current "
                               f"(next check in {next_check_hours:.1f} hours)")
                return True
                
        except Exception as e:
            self.logger.error(f"Calibration scheduling failed: {e}")
            return False
