from pathlib import Path


def datafile_exists(id: str, root: Path) -> bool:
    """
    Determine whether the datafile already exists in the tree.
    """
    g = root.glob(f"**/data_{id}.json")
    return next(g, None) is not None
