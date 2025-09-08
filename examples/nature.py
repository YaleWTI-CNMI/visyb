import math
import random
import numpy as np
from visyb.processor.definitions import BuilderPlot, modcont, plot_generator
import time

nature_tsv = open(
    "C:\\Users\\Alex\\Documents\\GitHub\\visyb\\examples\\sensitive\\nature-journal-136k.tsv",
    "r",
    encoding="utf-8",
)
nature_data = nature_tsv.readlines()
nature_tsv.close()
nature_data = [line.strip().split("\t") for line in nature_data[1:]]  # type: ignore # skip header


@plot_generator
def nature_test(zvariance: modcont(range=[0, 50], step=1) = 0, sizeamplifier: modcont(range=[1, 1.5], step=0.01) = 1):  # type: ignore
    start_time = time.time()

    # Headers: pid	date	journal	title	abstract	mesh_terms	x	y	citation_count	size	year	pmcid	mesh_topics

    # Compute min and max citation counts
    citation_counts = [int(float(row[8])) for row in nature_data]

    min_cite = math.log10(min(citation_counts) + 1)
    max_cite = math.log10(
        max(citation_counts) if max(citation_counts) != min_cite else min_cite + 1
    )

    print("Min citation count:", min_cite)
    print("Max citation count:", max_cite)

    def lerp(a, b, t):
        return a + (b - a) * t

    column_data = {
        "x": [float(row[6]) for row in nature_data],
        "y": [float(row[7]) for row in nature_data],
        "z": [50 + random.uniform(-zvariance, zvariance) for _ in nature_data],
        "size": [
            pow(lerp(0.001, 0.004, (math.log10(int(float(row[8])) + 1) - min_cite) / (max_cite - min_cite)), sizeamplifier)
            for row in nature_data
        ],
        "color": [
            {
                "r": lerp(0.0, 1.0, (math.log10(int(float(row[8])) + 1) - min_cite) / (max_cite - min_cite)),
                "g": 0.0,
                "b": 1.0 - lerp(0.0, 1.0, (math.log10(int(float(row[8])) + 1) - min_cite) / (max_cite - min_cite)),
            }
            for row in nature_data
        ],
    }

    builder = BuilderPlot(
        xlim=[min(column_data["x"]), max(column_data["x"])],
        ylim=[min(column_data["y"]), max(column_data["y"])],
        zlim=[0, 100],
    )

    builder.add_point_set(
        x=column_data["x"],
        y=column_data["y"],
        z=column_data["z"],
        color=column_data["color"],
        size=column_data["size"],
    )

    elapsed_ms = (time.time() - start_time) * 1000
    print(f"Function execution time: {elapsed_ms:.2f} ms")

    return builder
