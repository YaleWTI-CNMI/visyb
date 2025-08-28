import random
import numpy as np
from visyb.processor.definitions import BuilderPlot, modcont, plot_generator


@plot_generator
def kuramoto_builder_test(zvariance: modcont(range=[0, 50], step=1) = 0):
    nature_tsv = open("C:\\Users\\Alex\\Documents\\GitHub\\visyb\\examples\\sensitive\\nature-journal-136k.tsv", "r", encoding="utf-8")
    nature_data = nature_tsv.readlines()
    nature_tsv.close()


    nature_data = [line.strip().split("\t") for line in nature_data[1:]]  # skip header

    # Headers: pid	date	journal	title	abstract	mesh_terms	x	y	citation_count	size	year	pmcid	mesh_topics

    # build column arrays
    column_data = {
        "x": [float(row[6]) for row in nature_data],
        "y": [float(row[7]) for row in nature_data],
        "z": [50 + random.uniform(-zvariance, zvariance) for _ in nature_data],
    }

    builder = BuilderPlot(xlim=[min(column_data["x"]), max(column_data["x"])],
                          ylim=[min(column_data["y"]), max(column_data["y"])],
                          zlim=[0, 100])

    builder.add_point_set(x=column_data["x"],
                          y=column_data["y"],
                          z=column_data["z"])

    return builder
