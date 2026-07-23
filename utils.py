import random


def read_trace(file):
    """
    Reads a trace file.

    Expected format

    10 Read
    25 Write
    """

    trace = []

    for line in file:

        line = line.decode().strip()

        if not line:
            continue

        address, operation = line.split()

        trace.append(
            (
                int(address),
                operation,
            )
        )

    return trace


def generate_random_trace(length=20):
    """
    Generates a random memory trace.
    """

    trace = []

    for _ in range(length):

        trace.append(

            (
                random.randint(0, 255),

                random.choice(
                    [
                        "Read",
                        "Write",
                    ]
                ),
            )

        )

    return trace