#%% Function to insert sub arrays into a larger array
def insert_subarray(A_large, A_small, indices):
    '''
    # A_large: pre-allocated main sympy array to insert a sympy sub-array
    # A_small: A sympy sub-array to fill into A_large
    # indices: Indices where A_small shall be filled into A_large ([rows],[cols])
    '''

    row_idx, col_idx = indices

    # Column vector
    if A_small.rows != 1 and A_small.cols == 1:
        for i, r in enumerate(row_idx):
            A_large[r, col_idx[0]] += A_small[i, 0]
    
    # row vector
    elif A_small.rows == 1 and A_small.cols != 1:
        for i, r in enumerate(col_idx): 
            A_large[row_idx[0], r] += A_small[0, i]

    # Full array
    else:  
        for i, r in enumerate(row_idx):
            for j, c in enumerate(col_idx):
                A_large[r, c] += A_small[i, j]

#%% Function to sort letters and numbers within a list
def sort_key(sym):
    import re

    match = re.match(r"([a-zA-Z]+)(\d+)", sym.name)  # Extract prefix and number
    if match:
        prefix, num = match.groups()
        return (prefix, int(num))  # Sort alphabetically, then numerically
    return (sym.name, 0)  # Default case (if no match)

#%% Function to convert sympy expressions to a numerical framework (Numpy, Jax, etc.)
def function_save(FileName, functions_to_save, module):
    '''
    # FileName:          Name of the generated .py file
    # functions_to_save: A Python Dictonary of varibale name and the lambdified function "{var: lambdified_func}"
    # module:            Set the numerical framework "numpy", "jax" etc.
    '''

    import inspect
    import ast
    import importlib

    # Importing module (Switch to include e.g., jax or numpy)
    if module == "jax":
        module = "jax.numpy"
    # Import the module dynamically
    try:
        mod = importlib.import_module(module)
    except ImportError:
        print(f"Error: Module '{module}' could not be imported.")
        return

    # Write module import statement at the beginning of the file
    with open(FileName, "w") as file:
        file.write(f"import {module}\n\n")

    # Extracting source code adding prefix (e.g., numpy.cos or jax.numpy.sin)
    functions = {}

    # Looping though each function
    for name, func in functions_to_save.items():
        Module_attribute = set()

        # Obtaining the source code along with it's abtract syntax tree (ast)
        source_code = inspect.getsource(func) 
        tree = ast.parse(source_code) 
        input_params = list(inspect.signature(func).parameters.keys())

        # Walk through the AST to detect module attributes
        for node in ast.walk(tree):
            # Check if instance contain a "Name" e.g., "Name(id='x')" or "Name(id='cos')" AND check if "id" within said "Name" exists in the module
            if isinstance(node, ast.Name) and hasattr(node, "id") and node.id in dir(mod):
                if node.id in input_params:  # Avoid prefixing input parameters
                    print(f"Warning! Input parameter '{node.id}' conflicts with '{module}'. Ignoring prefix.")
                elif f"{module}.{node.id}" not in source_code:  # Avoid duplicate prefixing
                    Module_attribute.add(node.id)
                    source_code = source_code.replace(node.id, f"{module}.{node.id}")

        # Store modified function source and rename it
        functions[name] = source_code.replace('_lambdifygenerated', name)

        # Append modified function to the file
        with open(FileName, "a") as file:
            file.write(functions[name] + "\n")

        # Print detected attributes and final function source for debugging
        print('-' * 90)
        print(f"Detected attributes in function '{name}': {Module_attribute}\n")
        print(functions[name])