"""
External excitation functions for high-speed elevator systems.
Implements traction sheave eccentricity, reverse braking torque, and guide rail impacts.
"""

import numpy as np


class ExcitationGenerator:
    """Generate three types of external excitations for elevator dynamics."""

    def __init__(self, velocity=6.0, total_time=10.0, dt=0.01):
        """
        Initialize excitation generator.

        Parameters
        ----------
        velocity : float
            Steady-state elevator velocity (m/s)
        total_time : float
            Total simulation time (s)
        dt : float
            Time step (s)
        """
        self.velocity = velocity
        self.total_time = total_time
        self.dt = dt
        self.t = np.arange(0, total_time, dt)
        self.eccentricity_mm = 3.0  # 3 mm eccentricity
        self.sheave_radius = 0.3  # m

    def eccentric_excitation(self):
        """
        Traction sheave eccentricity excitation.

        Returns
        -------
        excitation : ndarray
            Displacement excitation from eccentric rotation
        """
        # Rotation frequency: f = v / (2 * pi * r)
        rotation_freq = self.velocity / (2 * np.pi * self.sheave_radius)
        angular_velocity = 2 * np.pi * rotation_freq

        # Vertical component of eccentric motion
        u1 = (self.eccentricity_mm / 1000.0) * np.cos(angular_velocity * self.t)

        return u1

    def reverse_braking_excitation(self):
        """
        Reverse braking torque excitation during deceleration phase.
        Piecewise profile: rise -> steady-state -> decay -> zero.

        Returns
        -------
        excitation : ndarray
            Torque-induced longitudinal force on traction system
        """
        M_max = 5000.0  # Maximum reverse torque (N·m)
        r_sheave = 0.3  # Sheave radius (m)
        F_max = M_max / r_sheave  # Convert to force

        # Time phases
        t1 = 0.5  # Rise time
        t2 = 2.5  # Steady-state end
        t3 = 4.0  # Decay end
        decay_rate = 0.5

        excitation = np.zeros_like(self.t)

        for i, ti in enumerate(self.t):
            if ti < t1:
                # Rise phase
                excitation[i] = F_max * (ti / t1)
            elif ti < t2:
                # Steady-state phase
                excitation[i] = F_max
            elif ti < t3:
                # Decay phase with exponential decay
                decay_time = ti - t2
                excitation[i] = F_max * np.exp(-decay_rate * decay_time)
            else:
                excitation[i] = 0.0

        return excitation

    def rail_joint_impact_excitation(self):
        """
        Vertical impact excitation from passing over guide rail joints.
        Modeled as piecewise impulses at regular intervals.

        Returns
        -------
        excitation : ndarray
            Vertical displacement impulses from rail joints
        """
        joint_spacing = 1.0  # Standard rail segment length (m)
        gap_height = 0.001  # Typical joint gap (m)

        # Time interval between joints
        joint_period = joint_spacing / self.velocity

        excitation = np.zeros_like(self.t)
        joint_count = int(self.total_time / joint_period)

        for n in range(joint_count):
            joint_time = n * joint_period
            # Impulse duration is very short (contact time)
            contact_duration = 0.001  # 1 ms contact time
            t_start = joint_time
            t_end = joint_time + contact_duration
            contact_indices = np.where((self.t >= t_start) & (self.t < t_end))[0]

            if len(contact_indices) > 0:
                # Displacement pulse (triangular shape)
                pulse_amp = gap_height * (self.velocity / 2.0)  # Higher velocity -> higher impact
                excitation[contact_indices] = pulse_amp

        return excitation

    def combined_excitation(self, load_ratio=1.0):
        """
        Generate combined excitation from all three sources.

        Parameters
        ----------
        load_ratio : float
            Load factor (0 = no load, 1.0 = full load). Scales impact magnitudes.

        Returns
        -------
        dict
            Dictionary with 'eccentric', 'braking', 'rail_impact', 'combined' keys
        """
        ecc = self.eccentric_excitation()
        braking = self.reverse_braking_excitation()
        rail = self.rail_joint_impact_excitation()

        # Scale by load ratio
        rail_scaled = rail * (1.0 + 0.5 * load_ratio)  # Load increases impact severity

        return {
            "time": self.t,
            "eccentric": ecc,
            "braking": braking,
            "rail_impact": rail_scaled,
            "combined": ecc + braking + rail_scaled,
        }
