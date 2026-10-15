"""Dynamic parameter optimization for traction-type elevators using genetic algorithms.

Implements a dynamic byte coding genetic algorithm to optimize elevator dynamic parameters
(spring stiffness and damping coefficients) to minimize vertical vibration acceleration.
"""

from collections.abc import Callable

import numpy as np


class ElevatorDynamicModel:
    """9-DOF vertical dynamic model of a 2:1 traction-type passenger elevator."""

    def __init__(
        self,
        masses: np.ndarray,
        inertias: np.ndarray,
        stiffness: np.ndarray,
        damping: np.ndarray,
    ):
        """Initialize the elevator dynamic model.

        Args:
            masses: Array of 6 masses [m1..m6] (kg)
            inertias: Array of 3 rotational inertias [I1..I3] (kg·m²)
            stiffness: Array of 6 stiffness coefficients [k0..k5] (N/m)
            damping: Array of 6 damping coefficients [c0..c5] (N·s/m)
        """
        self.masses = masses
        self.inertias = inertias
        self.stiffness = stiffness
        self.damping = damping
        self.radii = np.array([0.5, 0.45, 0.4])

    def compute_response(self, time: np.ndarray, excitation: np.ndarray) -> np.ndarray:
        """Compute vibration response under excitation.

        Args:
            time: Time vector (s)
            excitation: Excitation force vector (N)

        Returns:
            Vertical vibration acceleration of elevator cage (m/s²)
        """
        # Simplified modal response computation
        modal_mass = np.sum(self.masses) * 0.5
        modal_stiffness = np.sum(self.stiffness) * 0.3
        modal_damping = np.sum(self.damping) * 0.2

        omega_n = np.sqrt(modal_stiffness / modal_mass)
        zeta = modal_damping / (2 * np.sqrt(modal_stiffness * modal_mass))

        acceleration = np.zeros_like(time)
        for i, force in enumerate(excitation):
            if omega_n > 0:
                response = (force / modal_mass) * np.exp(-zeta * omega_n * time[i])
                acceleration[i] = response

        return acceleration

    def objective_function(self, excitation: np.ndarray) -> float:
        """Compute objective function: peak acceleration response.

        Args:
            excitation: Excitation force vector (N)

        Returns:
            Peak acceleration (m/s²)
        """
        time = np.linspace(0, 1, len(excitation))
        response = self.compute_response(time, excitation)
        return np.max(np.abs(response))


class DynamicByteCodedGA:
    """Dynamic byte coding genetic algorithm for parameter optimization."""

    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.9,
    ):
        """Initialize the genetic algorithm.

        Args:
            population_size: Number of individuals per generation
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation per gene
            crossover_rate: Probability of crossover
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def encode_parameters(self, params: np.ndarray) -> np.ndarray:
        """Encode continuous parameters to byte-coded chromosome.

        Args:
            params: Continuous parameters

        Returns:
            Byte-encoded chromosome
        """
        normalized = (params - np.min(params)) / (np.max(params) - np.min(params))
        return (normalized * 255).astype(np.uint8)

    def decode_parameters(
        self, chromosome: np.ndarray, min_vals: np.ndarray, max_vals: np.ndarray
    ) -> np.ndarray:
        """Decode byte-coded chromosome to continuous parameters.

        Args:
            chromosome: Byte-encoded chromosome
            min_vals: Minimum parameter values
            max_vals: Maximum parameter values

        Returns:
            Continuous parameters
        """
        normalized = chromosome.astype(float) / 255.0
        return min_vals + normalized * (max_vals - min_vals)

    def mutate(self, chromosome: np.ndarray) -> np.ndarray:
        """Apply dynamic mutation.

        Args:
            chromosome: Byte-encoded chromosome

        Returns:
            Mutated chromosome
        """
        mutated = chromosome.copy()
        for i in range(len(mutated)):
            if np.random.random() < self.mutation_rate:
                mutation_amount = np.random.randint(-10, 11)
                mutated[i] = np.clip(mutated[i] + mutation_amount, 0, 255).astype(np.uint8)
        return mutated

    def crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Single-point crossover.

        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome

        Returns:
            Two offspring chromosomes
        """
        if np.random.random() < self.crossover_rate:
            point = np.random.randint(1, len(parent1))
            child1 = np.concatenate([parent1[:point], parent2[point:]])
            child2 = np.concatenate([parent2[:point], parent1[point:]])
            return child1.astype(np.uint8), child2.astype(np.uint8)
        return parent1.copy(), parent2.copy()

    def optimize(
        self,
        objective: Callable[[np.ndarray], float],
        n_params: int,
        min_vals: np.ndarray,
        max_vals: np.ndarray,
    ) -> tuple[np.ndarray, list]:
        """Run the genetic algorithm optimization.

        Args:
            objective: Objective function to minimize
            n_params: Number of parameters to optimize
            min_vals: Minimum parameter bounds
            max_vals: Maximum parameter bounds

        Returns:
            Tuple of (best_parameters, fitness_history)
        """
        population = np.random.randint(0, 256, (self.population_size, n_params), dtype=np.uint8)
        fitness_history = []

        for _generation in range(self.generations):
            fitness_scores = []
            for individual in population:
                params = self.decode_parameters(individual, min_vals, max_vals)
                fitness = objective(params)
                fitness_scores.append(fitness)

            fitness_scores = np.array(fitness_scores)
            fitness_history.append(np.min(fitness_scores))

            best_idx = np.argmin(fitness_scores)
            best_individual = population[best_idx].copy()

            probabilities = 1.0 / (1.0 + fitness_scores)
            probabilities /= np.sum(probabilities)

            selected_indices = np.random.choice(
                self.population_size, self.population_size, p=probabilities
            )
            new_population = []

            for i in range(0, self.population_size - 1, 2):
                idx1, idx2 = selected_indices[i], selected_indices[i + 1]
                child1, child2 = self.crossover(population[idx1], population[idx2])
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])

            if self.population_size % 2 == 1:
                idx1 = selected_indices[-1]
                child1 = self.mutate(population[idx1].copy())
                new_population.append(child1)

            population = np.array(new_population[: self.population_size], dtype=np.uint8)
            population[0] = best_individual

        best_individual = population[0]
        best_params = self.decode_parameters(best_individual, min_vals, max_vals)

        return best_params, fitness_history
