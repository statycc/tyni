import os


def ensure_path(fn):
    dir_path, _ = os.path.split(fn)
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def attr_of(obj, type_):
    return [x for x in dir(obj) if
            isinstance(getattr(obj, x), type_)]
