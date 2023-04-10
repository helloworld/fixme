import hashlib
import os
import pickle

from fixme.console import console


def memoize_function_to_disk(func):
    def wrapper(*args, **kwargs):
        arg_hash = hashlib.sha256((str(args) + str(kwargs)).encode()).hexdigest()

        cache_dir = file_relative_path(__file__, ".cache")
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)

        filename = func.__name__ + "_" + arg_hash
        filename = os.path.join(cache_dir, filename)

        if os.path.isfile(filename):
            console.print("[bold blue]Loading from cache...[/bold blue]]")
            with open(filename, "rb") as f:
                result = pickle.load(f)
        else:
            result = func(*args, **kwargs)
            with open(filename, "wb") as f:
                pickle.dump(result, f)

        return result

    return wrapper


def file_relative_path(dunderfile: str, relative_path: str) -> str:
    return os.path.join(os.path.dirname(dunderfile), relative_path)
