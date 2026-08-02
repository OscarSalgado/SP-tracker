"""
Generate synthetic data for high-speed elevator vibration analysis.
Simulates elevator response to three excitation sources at different load conditions.
"""

import pickle
from pathlib import Path

import numpy as np

from .elevator_model import ElevatorMDOFModel
from .excitations import ExcitationGenerator
from .solver import solve_elevator_dynamics


def get_default_parameters():
    """Return typical high-speed elevator parameters from Tian et al. Table 2."""
    return {
        # Masses (kg)
        "m_motor": 198.45,
        "m_traction": 2835,
        "m_car_frame": 2282,
        "m_cabin": 1805,
        "m_counterweight": 4887.4,
        # Stiffness (N/m)
        "k_rope_car": 2.72e5,
        "k_rope_counter": 2.72e5,
        "k_isolation": 9.8e5,
        "rope_stiffness": 1.176e11,  # Young's modulus * cross-section
        # Damping (N·s/m)
        "c_rope_car": 1000,
        "c_rope_counter": 1000,
        "c_isolation": 2000,
        "damping": 500,
    }


def generate_scenario(scenario_name, load_ratio, velocity=6.0, duration=10.0, dt=0.01):
    """
    Generate synthetic data for a specific scenario.

    Parameters
    ----------
    scenario_name : str
        Name of scenario ('no_load', 'half_load', 'full_load')
    load_ratio : float
        Load factor (0, 0.5, or 1.0)
    velocity : float
        Elevator velocity (m/s)
    duration : float
        Simulation duration (s)
    dt : float
        Time step (s)

    Returns
    -------
    dict
        Complete simulation results with time, accelerations, forces, stresses
    """
    print(f"  Generating {scenario_name}...")

    # Setup
    params = get_default_parameters()
    time = np.arange(0, duration, dt)

    # Create model and generate excitations
    model = ElevatorMDOFModel(params)
    exc_gen = ExcitationGenerator(velocity=velocity, total_time=duration, dt=dt)
    excitations = exc_gen.combined_excitation(load_ratio=load_ratio)

    # Solve dynamics
    solution = solve_elevator_dynamics(model, time, excitations, load_ratio)

    # Extract car acceleration (DOF 1 is car displacement)
    car_accel = solution["acceleration"][:, 1]

    # Compute wire rope stress (simplified: proportional to rope tension + dynamic effects)
    base_stress = 150 + load_ratio * 450  # Static stress based on load
    dynamic_stress = base_stress + 50 * np.abs(solution["velocity"][:, 1])
    rope_stress = np.clip(dynamic_stress, 0, 750)  # Clamp to realistic range

    return {
        "time": time,
        "scenario": scenario_name,
        "load_ratio": load_ratio,
        "car_acceleration": car_accel,
        "rope_stress": rope_stress,
        "excitations": {
            "eccentric": excitations["eccentric"],
            "braking": excitations["braking"],
            "rail_impact": excitations["rail_impact"],
        },
        "natural_frequencies": model.compute_natural_frequencies(),
    }


def main():
    """Generate and save all synthetic datasets."""
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    print("Generating synthetic elevator dynamics data...")

    scenarios = [
        ("no_load", 0.0),
        ("half_load", 0.5),
        ("full_load", 1.0),
    ]

    all_results = {}

    for scenario_name, load_ratio in scenarios:
        result = generate_scenario(scenario_name, load_ratio)
        all_results[scenario_name] = result

    # Save to pickle
    output_file = output_dir / "synthetic_elevator_data.pkl"
    with open(output_file, "wb") as f:
        pickle.dump(all_results, f)

    print(f"Data saved to {output_file}")

    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 70)

    for scenario_name, result in all_results.items():
        accel = result["car_acceleration"]
        stress = result["rope_stress"]

        print(f"\n{scenario_name.upper()}")
        print(f"  Car acceleration:  peak = {np.max(np.abs(accel)):.3f} mm/s²")
        print(f"  Rope stress:       peak = {np.max(stress):.1f} MPa")
        print(f"  Natural frequencies: {result['natural_frequencies']}")

    return all_results
