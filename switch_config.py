import shutil
import sys

if len(sys.argv) != 2:
    print("Usage: python switch_config.py <scenario>")
    sys.exit(1)

scenario = sys.argv[1]

shutil.copy(
    f"configs/{scenario}.json",
    "config.json"
)

print(f"Loaded {scenario}")