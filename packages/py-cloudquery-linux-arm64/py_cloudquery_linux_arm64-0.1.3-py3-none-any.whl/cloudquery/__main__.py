import os
import sys
import subprocess

def main(args=None):
    here = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(here, 'bin', 'cloudquery')
    if not os.path.isfile(bin_path):
        print(f"cloudquery binary not found at {bin_path}", file=sys.stderr)
        sys.exit(1)
    if args is None:
        args = sys.argv[1:]
    result = subprocess.run([bin_path] + args)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
