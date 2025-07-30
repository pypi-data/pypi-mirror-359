"""
Python only helpers
"""

from datetime import datetime


def pathsafenow() -> str:
    """Convert the current datetime into a safe string to be used as a directory name, useful
    when stashing data.

    Returns:
        str: A safe directory name string representing the current datetime.

    Example:
        .. ipython:: python

            from ourtils.general import pathsafenow
            pathsafenow()
    """
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_datetime


def print_params(obj, *args) -> None:
    """Prints out the value of each arg from obj


    Example:
        .. ipython:: python

            from ourtils.general import print_params
            class Person:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age
                def say_hello(self, formal=False):
                    if formal:
                        return f'Welcome, {self.name}.'
                    else:
                        return f'Hey {self.name}!'
            person = Person('spongebob', 100)
            print_params(person, 'name', 'age', 'say_hello()', {'say_hello': {'formal': True}})
    """
    print(f"Summary for {obj}")
    for arg in args:
        if isinstance(arg, dict):
            keys = list(arg.keys())
            if len(keys) > 1:
                raise ValueError("Method dicts are expected to have a single key!")
            method_name = keys[0].replace("()", "")
            method_kwargs = arg[method_name]
            val = getattr(obj, method_name)(**method_kwargs)
        elif arg.lower().endswith("()"):
            method_name = arg.replace("()", "")
            val = getattr(obj, method_name)()
        else:
            val = getattr(obj, arg)
        print(f"{arg}: {val}")


def qatl(obj) -> list:
    """Quick attribute list, filters out private / dunders"""
    return [attr for attr in dir(obj) if not attr.startswith("_")]
