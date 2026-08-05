# Explainable Fault Classification with Kolmogorov-Arnold Networks

## Objective
Develop lightweight, interpretable models for bearing fault diagnosis and severity classification using Kolmogorov-Arnold Networks (KAN), prioritizing explainability without sacrificing detection accuracy.

## Method
1. **Kolmogorov-Arnold Network Architecture**: Shallow network with learnable univariate activation functions per edge.
2. **Automatic Feature Selection**: Identifies most discriminative features from vibration signals.
3. **Hyperparameter Tuning**: Optimizes network depth, activation functions, and regularization.
4. **Interpretability Mechanisms**: Provides feature attribution and symbolic representation of activation functions.
5. **Fault Classification**: Multi-class classification (Healthy, Inner Race, Outer Race, Ball, Combination).
6. **Severity Assessment**: Estimates degradation level for detected faults.

## Key Results
- **Explainability**: Produces interpretable models with explicit feature importance.
- **Lightweight**: Minimal number of selected features reduces computational cost and model complexity.
- **Accuracy**: Achieves competitive fault classification accuracy with superior interpretability.
- **Symbolic Activation Functions**: Enables symbolic representation of learned decision boundaries.

## Limitations
- Shallow network architecture may limit capacity for complex patterns.
- Automatic feature selection assumes features are separable in input space.
- Interpretability claims depend on feature meaningfulness.
- Validation primarily on laboratory bearing datasets.
