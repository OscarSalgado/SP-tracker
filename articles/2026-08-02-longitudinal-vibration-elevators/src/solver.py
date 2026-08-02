"""
Numerical solver for MDOF elevator dynamics using 4th-order Runge-Kutta integration.
Implements variable step-size RK4 method as described in Tian et al. (2026).
"""

import numpy as np


class RK4Solver:
    """
    4th-order Runge-Kutta solver for state-space system dz/dt = A*z + B*u(t).
    """

    def __init__(self, A, B, z0):
        """
        Initialize RK4 solver.

        Parameters
        ----------
        A : ndarray, shape (2n, 2n)
            State transition matrix
        B : ndarray, shape (2n, 1)
            Input matrix
        z0 : ndarray, shape (2n,)
            Initial state [x, dx/dt]^T
        """
        self.A = A
        self.B = B
        self.z = z0.copy()
        self.history = [z0.copy()]

    def _dynamics(self, z, u):
        """Compute dz/dt = A*z + B*u."""
        return self.A @ z + self.B.flatten() * u

    def step(self, u, dt):
        """
        Perform one RK4 step.

        Parameters
        ----------
        u : float
            Input (force) at current time
        dt : float
            Time step

        Returns
        -------
        z : ndarray
            New state after step
        """
        z = self.z

        k1 = self._dynamics(z, u)
        k2 = self._dynamics(z + 0.5 * dt * k1, u)
        k3 = self._dynamics(z + 0.5 * dt * k2, u)
        k4 = self._dynamics(z + dt * k3, u)

        self.z = z + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        self.history.append(self.z.copy())

        return self.z

    def integrate(self, time, excitation_func):
        """
        Integrate system over specified time with excitation input.

        Parameters
        ----------
        time : ndarray
            Time points (s)
        excitation_func : callable
            Function that returns force given time t

        Returns
        -------
        dict
            Solutions with 'time', 'displacement', 'velocity', 'acceleration' keys
        """
        dt_base = time[1] - time[0]
        displacements = [self.history[0][: len(self.history[0]) // 2]]
        velocities = [self.history[0][len(self.history[0]) // 2 :]]
        times = [time[0]]

        for t in time[1:]:
            u = excitation_func(t)
            self.step(u, dt_base)
            times.append(t)

            n_dof = len(self.z) // 2
            displacements.append(self.z[:n_dof])
            velocities.append(self.z[n_dof:])

        displacements = np.array(displacements)
        velocities = np.array(velocities)

        # Compute accelerations numerically
        accelerations = np.gradient(velocities, time, axis=0)

        return {
            "time": np.array(times),
            "displacement": displacements,
            "velocity": velocities,
            "acceleration": accelerations,
        }


def solve_elevator_dynamics(model, time, excitation, load_ratio=1.0):
    """
    Solve elevator MDOF dynamics for given excitation.

    Parameters
    ----------
    model : ElevatorMDOFModel
        Assembled elevator model
    time : ndarray
        Time vector for integration
    excitation : dict
        Excitation dictionary from ExcitationGenerator.combined_excitation()
    load_ratio : float
        Load factor (0-1)

    Returns
    -------
    dict
        Solutions dict with displacement, velocity, acceleration, time
    """
    A, B = model.state_space_matrices()
    n_dof = model.M.shape[0]
    z0 = np.zeros(2 * n_dof)

    # Create excitation interpolation function
    from scipy.interpolate import interp1d

    exc_func = interp1d(
        excitation["time"], excitation["combined"], kind="linear", fill_value="extrapolate"
    )

    solver = RK4Solver(A, B, z0)
    solution = solver.integrate(time, exc_func)

    return solution
