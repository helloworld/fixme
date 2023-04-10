# pylint: disable=print-call
import argparse
import subprocess
from typing import List

# We allow extra packages to be passed in via the command line because pip's version
# resolution requires everything to be installed at the same time.

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", action="count")
parser.add_argument(
    "packages",
    type=str,
    nargs="*",
    help="Additional packages (with optional version reqs) to pass to `pip install`",
)
parser.add_argument(
    "--install-examples",
    default=False,
    action="store_true",
    help="Install examples as well as core packages",
)


def main(
    quiet: bool,
    extra_packages: List[str],
    install_examples: bool,
) -> None:
    install_targets: List[str] = [
        *extra_packages,
    ]

    install_targets += [
        "-e .[black,pyright,ruff,test]",
    ]

    if install_examples:
        install_targets += [
            "-e examples/python_modules/syntax_error",
        ]

    # NOTE: These need to be installed as one long pip install command, otherwise pip
    # will install conflicting dependencies, which will break pip freeze snapshot
    # creation during the integration image build!
    cmd = ["pip", "install", *install_targets]

    if quiet is not None:
        cmd.append(f'-{"q" * quiet}')

    p = subprocess.Popen(
        " ".join(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    print(" ".join(cmd))
    while True:
        output = p.stdout.readline()  # type: ignore
        if p.poll() is not None:
            break
        if output:
            print(output.decode("utf-8").strip())


if __name__ == "__main__":
    args = parser.parse_args()
    main(
        quiet=args.quiet,
        extra_packages=args.packages,
        install_examples=args.install_examples,
    )
