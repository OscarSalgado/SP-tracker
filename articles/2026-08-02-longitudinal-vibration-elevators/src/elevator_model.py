"""
MDOF Dynamic model for high-speed elevator longitudinal vibration analysis.
Implements substructure assembly method from Tian et al. (2026).
"""

import numpy as np


class ElevatorMDOFModel:
    """
    Multi-degree-of-freedom model for elevator longitudinal dynamics.

    Degrees of freedom:
    - x1: traction machine displacement
    - x2: contact point (car-side rope)
    - x3: contact point (counterweight-side rope)
    - x4-x5: car and car frame displacements
    - x6-x10: rope segment contact points and suspension points
    - x11-x14: discretized traction and compensation rope displacements
    """

    def __init__(self, params):
        """
        Initialize model with elevator parameters.

        Parameters
        ----------
        params : dict
            System parameters including masses, stiffnesses, damping coefficients
        """
        self.params = params
        self._assemble_global_matrices()

    def _assemble_global_matrices(self):
        """Assemble global mass, stiffness, damping matrices from substructures."""
        # Simplified 6-DOF system for computational efficiency
        # Full model in paper is 12 DOF with discretized ropes

        n_dof = 6

        # Mass matrix
        m1 = self.params["m_traction"] + self.params["m_motor"]  # Motor + traction
        m2 = self.params["m_car_frame"] + self.params["m_cabin"]  # Car + cabin
        m3 = self.params["m_counterweight"]  # Counterweight

        self.M = np.zeros((n_dof, n_dof))
        self.M[0, 0] = m1
        self.M[1, 1] = m2
        self.M[2, 2] = m3
        self.M[3:, 3:] = np.eye(n_dof - 3) * m1 * 0.1  # Rope segment masses (simplified)

        # Stiffness matrix (coupling between subsystems)
        k1 = self.params["k_rope_car"]  # Upper rope stiffness
        k2 = self.params["k_rope_counter"]  # Counterweight rope stiffness
        k3 = self.params["k_isolation"]  # Isolation rubber

        self.K = np.zeros((n_dof, n_dof))
        # Traction - car coupling
        self.K[0, 0] = k1
        self.K[0, 1] = -k1
        self.K[1, 0] = -k1
        self.K[1, 1] = k1 + k3
        # Car - counterweight coupling
        self.K[2, 2] = k2
        self.K[1, 2] = -k2 * 0.5
        self.K[2, 1] = -k2 * 0.5
        # Rope segment stiffness
        for i in range(3, n_dof):
            self.K[i, i] = self.params["rope_stiffness"] / ((n_dof - 2) ** 2)

        # Damping matrix
        c1 = self.params["c_rope_car"]
        c2 = self.params["c_rope_counter"]
        c3 = self.params["c_isolation"]

        self.C = np.zeros((n_dof, n_dof))
        self.C[0, 0] = c1
        self.C[0, 1] = -c1
        self.C[1, 0] = -c1
        self.C[1, 1] = c1 + c3
        self.C[2, 2] = c2
        self.C[1, 2] = -c2 * 0.5
        self.C[2, 1] = -c2 * 0.5
        for i in range(3, n_dof):
            self.C[i, i] = self.params["damping"] / ((n_dof - 2) ** 2)

    def state_space_matrices(self):
        """
        Convert M, C, K system to state-space form: dz/dt = A*z + B*u
        where z = [x, dx/dt]^T
        """
        n = self.M.shape[0]

        # A matrix: [0, I; -M^-1*K, -M^-1*C]
        M_inv = np.linalg.inv(self.M)

        A = np.zeros((2 * n, 2 * n))
        A[:n, n:] = np.eye(n)
        A[n:, :n] = -M_inv @ self.K
        A[n:, n:] = -M_inv @ self.C

        # B matrix: [0; M^-1] for force input
        B = np.zeros((2 * n, 1))
        B[n:, 0] = M_inv[:, 0]  # Force on traction system

        return A, B

    def compute_natural_frequencies(self):
        """Compute natural frequencies (Hz) from eigenvalue analysis."""
        eigenvalues = np.linalg.eigvals(-self.K) / (2 * np.pi)  # Simplified
        natural_freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
        return np.sort(natural_freqs[natural_freqs > 0])[:3]  # Return first 3 modes
