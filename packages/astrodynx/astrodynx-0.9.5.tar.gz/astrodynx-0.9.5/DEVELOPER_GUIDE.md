# AstroDynX Developer Guide

This guide provides detailed information for developers working on AstroDynX, complementing the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Architecture Overview

### Design Principles

AstroDynX is built on several key principles:

1. **JAX-First**: All numerical computations use JAX for automatic differentiation and acceleration
2. **Pure Functions**: Emphasis on functional programming for better composability
3. **Type Safety**: Comprehensive type hints for better developer experience
4. **Performance**: Optimized for GPU/TPU acceleration
5. **Modularity**: Clear separation of concerns between modules

### Core Dependencies

- **JAX**: Numerical computing, automatic differentiation, JIT compilation
- **Python 3.10+**: Modern Python features and type system

### Module Structure

```
astrodynx/
├── twobody/              # Two-body orbital mechanics
│   ├── kepler_equation.py    # Kepler's equation solvers
│   ├── orb_integrals.py      # Orbital integrals and elements
│   └── ivp.py                # Initial value problems
└── utils/                # Utility functions
    └── rotation_matrix.py    # Coordinate transformations
```

## JAX Development Guidelines

### Array Handling

Always use `jax.numpy` arrays:

```python
import jax.numpy as jnp
from jax import Array

# Good
def compute_distance(r1: Array, r2: Array) -> Array:
    return jnp.linalg.norm(r1 - r2)

# Avoid
import numpy as np
def compute_distance(r1: np.ndarray, r2: np.ndarray) -> np.ndarray:
    return np.linalg.norm(r1 - r2)
```

### JIT Compilation

Use `@jax.jit` for performance-critical functions:

```python
from jax import jit

@jit
def orbital_energy(position: Array, velocity: Array, mu: float) -> Array:
    """Calculate specific orbital energy."""
    r = jnp.linalg.norm(position)
    v_squared = jnp.sum(velocity**2)
    return 0.5 * v_squared - mu / r
```

### Vectorization

Design functions to work with both scalar and array inputs:

```python
@jit
def mean_motion(semi_major_axis: Array, mu: float) -> Array:
    """Calculate mean motion for scalar or array inputs."""
    return jnp.sqrt(mu / jnp.power(semi_major_axis, 3))

# Works with scalars
n_scalar = mean_motion(7000e3, 3.986004418e14)

# Works with arrays
a_array = jnp.array([7000e3, 8000e3, 9000e3])
n_array = mean_motion(a_array, 3.986004418e14)
```

### Gradient Computation

Ensure functions are differentiable:

```python
from jax import grad, jacfwd

def orbital_period(semi_major_axis: Array, mu: float) -> Array:
    return 2 * jnp.pi * jnp.sqrt(semi_major_axis**3 / mu)

# Compute gradient with respect to semi-major axis
dT_da = grad(orbital_period)(7000e3, 3.986004418e14)

# Compute Jacobian for vector inputs
jacobian = jacfwd(orbital_period)(jnp.array([7000e3, 8000e3]), 3.986004418e14)
```

## Testing Best Practices

### Test Organization

Follow the existing test structure:

```python
import pytest
import jax.numpy as jnp
from astrodynx.twobody import solve_kepler_equation

class TestKeplerEquation:
    """Test suite for Kepler equation functionality."""

    def test_circular_orbit(self):
        """Test circular orbit case (e=0)."""
        M = jnp.pi / 2
        e = 0.0
        E = solve_kepler_equation(M, e)
        assert jnp.allclose(E, M)

    @pytest.mark.parametrize("eccentricity", [0.1, 0.3, 0.5, 0.7, 0.9])
    def test_various_eccentricities(self, eccentricity):
        """Test solver across different eccentricities."""
        M = jnp.linspace(0, 2*jnp.pi, 100)
        E = solve_kepler_equation(M, eccentricity)

        # Verify Kepler's equation is satisfied
        computed_M = E - eccentricity * jnp.sin(E)
        assert jnp.allclose(computed_M, M, rtol=1e-12)
```

### Numerical Testing

For numerical algorithms, test:

1. **Known analytical solutions**
2. **Boundary conditions**
3. **Convergence properties**
4. **Numerical stability**

```python
def test_kepler_equation_convergence(self):
    """Test convergence for high eccentricity."""
    M = jnp.pi
    e = 0.99  # High eccentricity
    E = solve_kepler_equation(M, e, tolerance=1e-15)

    # Verify solution accuracy
    residual = E - e * jnp.sin(E) - M
    assert jnp.abs(residual) < 1e-14
```

### Performance Testing

Include performance benchmarks:

```python
import time

def test_kepler_solver_performance(self):
    """Benchmark Kepler equation solver."""
    M = jnp.linspace(0, 2*jnp.pi, 10000)
    e = 0.5

    # JIT compile
    solve_kepler_equation(M[:10], e)

    # Benchmark
    start_time = time.time()
    result = solve_kepler_equation(M, e)
    end_time = time.time()

    assert end_time - start_time < 0.1  # Should be fast
    assert result.shape == M.shape
```

## Documentation Standards

### Docstring Format

Use NumPy-style docstrings with mathematical notation:

```python
def true_anomaly_from_eccentric(eccentric_anomaly: Array, eccentricity: Array) -> Array:
    """Convert eccentric anomaly to true anomaly.

    Uses the relationship:

    .. math::
        \\tan\\left(\\frac{\\nu}{2}\\right) = \\sqrt{\\frac{1+e}{1-e}} \\tan\\left(\\frac{E}{2}\\right)

    Parameters
    ----------
    eccentric_anomaly : Array
        Eccentric anomaly in radians.
    eccentricity : Array
        Orbital eccentricity (0 <= e < 1).

    Returns
    -------
    Array
        True anomaly in radians.

    Examples
    --------
    >>> import jax.numpy as jnp
    >>> E = jnp.pi / 2
    >>> e = 0.5
    >>> nu = true_anomaly_from_eccentric(E, e)
    >>> print(f"True anomaly: {nu:.4f} rad")
    True anomaly: 2.0344 rad

    References
    ----------
    .. [1] Curtis, H. D. (2013). Orbital Mechanics for Engineering Students.
    """
```

### Code Examples

Include practical examples in documentation:

```python
# In docstrings or tutorials
"""
Example: Satellite orbit analysis
---------------------------------

Calculate orbital elements for a satellite:

>>> import jax.numpy as jnp
>>> import astrodynx as adx

>>> # Initial conditions
>>> r0 = jnp.array([7000e3, 0, 0])      # Position (m)
>>> v0 = jnp.array([0, 7.5e3, 0])      # Velocity (m/s)
>>> mu = 3.986004418e14                 # Earth's GM (m³/s²)

>>> # Calculate orbital elements
>>> elements = adx.twobody.cartesian_to_elements(r0, v0, mu)
>>> print(f"Semi-major axis: {elements.a/1000:.1f} km")
>>> print(f"Eccentricity: {elements.e:.4f}")
"""
```

## Performance Optimization

### JIT Compilation Best Practices

1. **Compile once, use many times**:

```python
# Pre-compile for expected input shapes
@jit
def propagate_orbit(r0: Array, v0: Array, t: Array, mu: float) -> tuple[Array, Array]:
    # Implementation
    pass

# Warm up JIT
dummy_r = jnp.zeros(3)
dummy_v = jnp.zeros(3)
dummy_t = jnp.linspace(0, 3600, 100)
propagate_orbit(dummy_r, dummy_v, dummy_t, 3.986004418e14)
```

2. **Avoid Python loops in JIT functions**:

```python
# Good: Use JAX operations
@jit
def compute_positions(times: Array, elements: Array) -> Array:
    return jax.vmap(position_at_time)(times, elements)

# Avoid: Python loops
def compute_positions_slow(times: Array, elements: Array) -> Array:
    positions = []
    for t in times:
        pos = position_at_time(t, elements)
        positions.append(pos)
    return jnp.array(positions)
```

### Memory Efficiency

1. **Use appropriate data types**:

```python
# Use float32 for GPU efficiency when precision allows
positions = jnp.array(data, dtype=jnp.float32)

# Use float64 for high-precision calculations
orbital_elements = jnp.array(data, dtype=jnp.float64)
```

2. **Minimize array copies**:

```python
# Good: In-place operations where possible
def normalize_vector(v: Array) -> Array:
    norm = jnp.linalg.norm(v)
    return v / norm

# Avoid unnecessary intermediate arrays
def inefficient_calculation(data: Array) -> Array:
    temp1 = data * 2
    temp2 = temp1 + 1
    temp3 = temp2 ** 2
    return temp3
```

## Error Handling

### Input Validation

Validate inputs for physical constraints:

```python
def solve_kepler_equation(mean_anomaly: Array, eccentricity: Array) -> Array:
    """Solve Kepler's equation with input validation."""
    # Validate eccentricity range
    if jnp.any(eccentricity < 0) or jnp.any(eccentricity >= 1):
        raise ValueError("Eccentricity must be in range [0, 1)")

    # Normalize mean anomaly to [0, 2π]
    M = jnp.mod(mean_anomaly, 2 * jnp.pi)

    # Solver implementation
    return _kepler_solver_impl(M, eccentricity)
```

### Numerical Stability

Handle edge cases and numerical issues:

```python
def safe_division(numerator: Array, denominator: Array, epsilon: float = 1e-15) -> Array:
    """Perform division with protection against division by zero."""
    safe_denom = jnp.where(jnp.abs(denominator) < epsilon, epsilon, denominator)
    return numerator / safe_denom
```

## Debugging Tips

### JAX Debugging

1. **Use `jax.debug.print()` in JIT functions**:

```python
from jax import debug

@jit
def debug_function(x: Array) -> Array:
    debug.print("Input value: {}", x)
    result = x ** 2
    debug.print("Result: {}", result)
    return result
```

2. **Disable JIT for debugging**:

```python
# Temporarily disable JIT
with jax.disable_jit():
    result = my_jit_function(input_data)
```

3. **Check for NaN/Inf values**:

```python
def check_array_health(arr: Array, name: str) -> None:
    """Check array for NaN or Inf values."""
    if jnp.any(jnp.isnan(arr)):
        raise ValueError(f"{name} contains NaN values")
    if jnp.any(jnp.isinf(arr)):
        raise ValueError(f"{name} contains Inf values")
```

## Release Checklist

Before releasing a new version:

1. **Code Quality**:
   - [ ] All tests pass
   - [ ] Code coverage > 90%
   - [ ] No linting errors
   - [ ] Type checking passes

2. **Documentation**:
   - [ ] API documentation updated
   - [ ] Examples work correctly
   - [ ] Changelog updated

3. **Performance**:
   - [ ] Benchmarks run successfully
   - [ ] No performance regressions

4. **Compatibility**:
   - [ ] Works with supported Python versions
   - [ ] JAX compatibility verified
   - [ ] GPU/TPU testing completed

This guide should help you contribute effectively to AstroDynX. For questions, please open an issue or discussion on GitHub.
