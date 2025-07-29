# Wrapped-Optimizations

## Description

`wrapped_optimizations` is a Python wrapper around some of SciPy's optimization functions. Instead of having one 1D array which contains all parameters to be optimized, the wrapped functions allow the parameters to be defined locally in the functions to be optimized.

## Installation

To install this package, use pip:

```bash
pip install wrapped_optimizations
```

## Usage

Here is a simple example of how to use Wrapped-Optimizations:

```python
from wrapped_optimizations import differential_evolution, eval_function

def func(use_param, use_const, use_print=False):
    # define a named parameter
    x = use_param((2), 'x', bounds=(-5, 5))
    # define an unnamed parameter
    y = use_param((2,2), bounds=(-5, 5))

    # define a (named) constant
    # equals `N = 3`, but with the advantage that the value also gets saved to result.x
    N = use_const(3, name='N')

    V = use_param((N), bounds=(0, 20))
    if use_print:
        print(f'V: {V}')
    return np.linalg.norm(x - 1)**2 + np.linalg.norm(y - 3)**2

result = differential_evolution(func)
# result.x now contains all the parameters and constants
# {
#   'x': array([1., 1.]),
#   'param_1': array([[3., 3.], [3., 3.]]),
#   'param_2': array([ 9.49532267, 16.89317493,  9.37888973]),
#   'N': 3
# }

# `func` can now be called, also with additional parameters being forwarded to `func`:
# eval_function(func, result.x, True)
```

## Requirements

Wrapped-Optimizations requires the following Python libraries:

- NumPy
- SciPy

## License

This project is licensed under the MIT License.