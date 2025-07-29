import numpy as np
import scipy.optimize

def _unflatten_params(params_list, shapes, names, const_names=None, const_values=None):
    """Unflattens the parameters from a list into a dictionary with the specified shapes and names."""
    params = {}
    items_consumed = 0
    for i, (shape, name) in enumerate(zip(shapes, names)):
        n_params = np.prod(shape)
        param = params_list[items_consumed:items_consumed + n_params].reshape(shape)
        name = f'param_{i}' if name is None else name
        params[name] = param
        items_consumed += n_params
    if const_names is not None and const_values is not None:
        for i, (value, name) in enumerate(zip(const_values, const_names)):
            name = f'const_{i}' if name is None else name
            params[name] = value
    return params

class WrappedFunction:
    def __init__(self, func_to_optimize, params_shape, params_names, const_names, const_values):
        self.func_to_optimize = func_to_optimize
        self.params_shape = params_shape
        self.params_names = params_names
        self.const_names = const_names
        self.const_values = const_values

    def __call__(self, params_list, *additional_args):
        params = _unflatten_params(params_list, self.params_shape, self.params_names, self.const_names, self.const_values)
        nth_parameter = 0
        def use_param(shape, name=None, bounds=(-np.inf, np.inf)):
            nonlocal nth_parameter
            index = f'param_{nth_parameter}' if name is None else name
            nth_parameter += 1
            return params[index]
        def use_const(value, name=None):
            return value
        return self.func_to_optimize(use_param, use_const, *additional_args)

def differential_evolution(func, **kwargs):
    params_shape = []
    params_names = []
    params_bounds = ([], [])
    constants_names = []
    constants_values = []
    
    def initial_use_param(shape, name=None, bounds=(-np.inf, np.inf)):
        params_shape.append(shape)
        params_names.append(name)
        lb_broadcasted = np.full(shape, bounds[0])
        ub_broadcasted = np.full(shape, bounds[1])
        params_bounds[0].append(lb_broadcasted.flatten())
        params_bounds[1].append(ub_broadcasted.flatten())
        # even though we don't care about `func`'s result during first run, let's nevertheless provide some meaningful values
        value = np.zeros(shape)
        value += np.select((lb_broadcasted == -np.inf) & (ub_broadcasted != np.inf), ub_broadcasted, 0)
        value += np.select((lb_broadcasted != -np.inf) & (ub_broadcasted == np.inf), lb_broadcasted, 0)
        value += np.select((lb_broadcasted != -np.inf) & (ub_broadcasted != np.inf), (lb_broadcasted + ub_broadcasted) / 2, 0)
        return value
    
    def initial_use_const(value, name=None):
        constants_names.append(name)
        constants_values.append(value)
        return value
    
    func(initial_use_param, initial_use_const, *kwargs.get('args', []))

    wrapped_func = WrappedFunction(func, params_shape, params_names, constants_names, constants_values)

    bounds = scipy.optimize.Bounds(np.concatenate(params_bounds[0]), np.concatenate(params_bounds[1]))
    result = scipy.optimize.differential_evolution(wrapped_func, bounds, **kwargs)
    result.x = _unflatten_params(result.x, params_shape, params_names, constants_names, constants_values)
    return result

def eval_function(func, params, *args, **kwargs):
    nth_parameter = 0
    def use_param(shape, name=None, bounds=(-np.inf, np.inf)):
        nonlocal nth_parameter
        index = f'param_{nth_parameter}' if name is None else name
        nth_parameter += 1
        return params[index]
    nth_constant = 0
    def use_const(value, name=None):
        nonlocal nth_constant
        index = f'const_{nth_constant}' if name is None else name
        nth_constant += 1
        return params[index]
    return func(use_param, use_const, *args, **kwargs)