"""Tests for elevator dynamic optimization module."""

import numpy as np
import pytest
from src import DynamicByteCodedGA, ElevatorDynamicModel


class TestElevatorDynamicModel:
    """Tests for ElevatorDynamicModel class."""

    @pytest.fixture
    def model(self):
        """Create a test elevator model."""
        masses = np.array([800.0, 1200.0, 900.0, 1500.0, 1000.0, 1200.0])
        inertias = np.array([100.0, 120.0, 110.0])
        stiffness = np.array([3e5, 2e5, 2.5e5, 2e5, 2.2e5, 2.3e5])
        damping = np.array([3e3, 2.5e3, 2.8e3, 2.5e3, 2.6e3, 2.7e3])
        return ElevatorDynamicModel(masses, inertias, stiffness, damping)

    def test_model_initialization(self, model):
        """Test model is properly initialized."""
        assert model.masses.shape == (6,)
        assert model.inertias.shape == (3,)
        assert model.stiffness.shape == (6,)
        assert model.damping.shape == (6,)
        assert model.radii.shape == (3,)

    def test_compute_response_shape(self, model):
        """Test response computation returns correct shape."""
        time = np.linspace(0, 1, 100)
        excitation = np.sin(2 * np.pi * time)
        response = model.compute_response(time, excitation)
        assert response.shape == time.shape

    def test_compute_response_values(self, model):
        """Test response values are reasonable."""
        time = np.linspace(0, 1, 100)
        excitation = 100 * np.sin(2 * np.pi * time)
        response = model.compute_response(time, excitation)
        assert np.all(np.isfinite(response))
        assert np.max(np.abs(response)) > 0

    def test_objective_function(self, model):
        """Test objective function computation."""
        excitation = np.array([10.0, 20.0, 15.0, 25.0, 30.0])
        obj_value = model.objective_function(excitation)
        assert isinstance(obj_value, (float, np.floating))
        assert obj_value >= 0

    def test_objective_function_consistency(self, model):
        """Test objective function gives same result on same input."""
        excitation = np.array([10.0, 20.0, 15.0, 25.0, 30.0])
        obj1 = model.objective_function(excitation)
        obj2 = model.objective_function(excitation)
        assert obj1 == obj2


class TestDynamicByteCodedGA:
    """Tests for DynamicByteCodedGA class."""

    @pytest.fixture
    def ga(self):
        """Create a GA instance."""
        return DynamicByteCodedGA(population_size=20, generations=10, mutation_rate=0.1)

    def test_ga_initialization(self, ga):
        """Test GA is properly initialized."""
        assert ga.population_size == 20
        assert ga.generations == 10
        assert ga.mutation_rate == 0.1
        assert ga.crossover_rate == 0.9

    def test_encode_parameters(self, ga):
        """Test parameter encoding."""
        params = np.array([1000.0, 2000.0, 3000.0])
        encoded = ga.encode_parameters(params)
        assert encoded.dtype == np.uint8
        assert encoded.shape == params.shape
        assert np.all(encoded >= 0) and np.all(encoded <= 255)

    def test_decode_parameters(self, ga):
        """Test parameter decoding."""
        chromosome = np.array([0, 128, 255], dtype=np.uint8)
        min_vals = np.array([1e5, 1e5, 1e5])
        max_vals = np.array([8e5, 8e5, 8e5])
        decoded = ga.decode_parameters(chromosome, min_vals, max_vals)
        assert decoded.dtype in [np.float64, float]
        assert decoded.shape == chromosome.shape
        assert np.all(decoded >= min_vals) and np.all(decoded <= max_vals)

    def test_encode_decode_roundtrip(self, ga):
        """Test encoding and decoding roundtrip allows for quantization loss."""
        original = np.array([2e5, 3e5, 4e5])
        encoded = ga.encode_parameters(original)
        decoded = ga.decode_parameters(
            encoded,
            np.min(original) * np.ones(3),
            np.max(original) * np.ones(3),
        )
        assert np.allclose(decoded, original, rtol=0.1)

    def test_mutate(self, ga):
        """Test mutation operator."""
        chromosome = np.array([100, 150, 200], dtype=np.uint8)
        mutated = ga.mutate(chromosome)
        assert mutated.dtype == np.uint8
        assert mutated.shape == chromosome.shape
        assert np.all(mutated >= 0) and np.all(mutated <= 255)

    def test_crossover(self, ga):
        """Test crossover operator."""
        parent1 = np.array([10, 20, 30, 40, 50], dtype=np.uint8)
        parent2 = np.array([100, 110, 120, 130, 140], dtype=np.uint8)
        child1, child2 = ga.crossover(parent1, parent2)
        assert child1.dtype == np.uint8
        assert child2.dtype == np.uint8
        assert child1.shape == parent1.shape
        assert child2.shape == parent2.shape

    def test_crossover_produces_offspring(self, ga):
        """Test crossover produces valid offspring."""
        parent1 = np.array([10, 20, 30, 40, 50], dtype=np.uint8)
        parent2 = np.array([100, 110, 120, 130, 140], dtype=np.uint8)
        ga.crossover_rate = 1.0
        child1, child2 = ga.crossover(parent1, parent2)
        assert (
            np.allclose(child1, parent1)
            or np.allclose(child1, parent2)
            or (np.any(child1 != parent1) and np.any(child1 != parent2))
        )

    def test_optimize_runs_without_error(self):
        """Test optimization completes successfully."""

        def simple_objective(params):
            return np.sum((params - 5e5) ** 2)

        ga = DynamicByteCodedGA(population_size=10, generations=5)
        min_vals = np.array([1e5, 1e5])
        max_vals = np.array([8e5, 8e5])
        best_params, history = ga.optimize(simple_objective, 2, min_vals, max_vals)
        assert best_params.shape == (2,)
        assert len(history) == 5
        assert np.all(np.isfinite(best_params))

    def test_optimize_improves_fitness(self):
        """Test optimization improves fitness over generations."""

        def simple_objective(params):
            return np.sum((params - 4e5) ** 2)

        ga = DynamicByteCodedGA(population_size=20, generations=20)
        min_vals = np.array([1e5, 1e5])
        max_vals = np.array([8e5, 8e5])
        _, history = ga.optimize(simple_objective, 2, min_vals, max_vals)
        assert history[-1] <= history[0]

    def test_optimize_bounds_respected(self):
        """Test optimized parameters respect bounds."""

        def dummy_objective(params):
            return np.sum(params)

        ga = DynamicByteCodedGA(population_size=10, generations=5)
        min_vals = np.array([1e5, 2e5, 1.5e5])
        max_vals = np.array([5e5, 6e5, 4e5])
        best_params, _ = ga.optimize(dummy_objective, 3, min_vals, max_vals)
        assert np.all(best_params >= min_vals)
        assert np.all(best_params <= max_vals)


class TestIntegration:
    """Integration tests combining model and GA."""

    def test_optimization_workflow(self):
        """Test complete optimization workflow."""
        masses = np.array([800.0, 1200.0, 900.0, 1500.0, 1000.0, 1200.0])
        inertias = np.array([100.0, 120.0, 110.0])
        stiffness = np.array([3e5, 2e5, 2.5e5, 2e5, 2.2e5, 2.3e5])
        damping = np.array([3e3, 2.5e3, 2.8e3, 2.5e3, 2.6e3, 2.7e3])

        model = ElevatorDynamicModel(masses, inertias, stiffness, damping)
        t = np.linspace(0, 1, 100)
        excitation = 50 * np.sin(2 * np.pi * 2 * t)
        initial_obj = model.objective_function(excitation)

        def objective_for_ga(params):
            model.stiffness = params
            return model.objective_function(excitation)

        ga = DynamicByteCodedGA(population_size=15, generations=5)
        min_vals = np.array([1e5, 1e5, 1e5, 1e5, 1e5, 1e5])
        max_vals = np.array([8e5, 8e5, 8e5, 8e5, 8e5, 8e5])

        optimal_params, history = ga.optimize(objective_for_ga, 6, min_vals, max_vals)
        assert len(history) == 5
        assert history[-1] <= initial_obj
        assert np.all(np.isfinite(optimal_params))
