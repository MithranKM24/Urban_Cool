import os


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_ROOT = os.path.abspath(
    os.path.expanduser(
        os.environ.get("URBANCOOL_DATA_DIR", os.path.join(REPOSITORY_ROOT, "data"))
    )
)
RAW_DATA_DIR = os.path.join(DATA_ROOT, "raw")
VALIDATED_DATA_DIR = os.path.join(DATA_ROOT, "validated")
