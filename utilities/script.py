import sys


def reader(shell, lines):
        for line in shell.stdout:
            lines.append(line)
            sys.stdout.write(line)
