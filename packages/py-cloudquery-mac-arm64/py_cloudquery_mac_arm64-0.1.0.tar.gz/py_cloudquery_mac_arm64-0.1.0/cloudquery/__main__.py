import os
import sys
import subprocess

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(here, 'bin', 'cloudquery')
    if not os.path.isfile(bin_path):
        print(f"cloudquery binary not found at {bin_path}", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([bin_path] + sys.argv[1:])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
