from flask import Flask, render_template, request
import numpy as np
from geopy.distance import great_circle
from ant_colony import AntColony
from utils import load_cities
import plotly.graph_objects as go
import json
import os
import signal

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_map", methods=["POST"])
def generate_map():
    data = request.get_json()
    region = data["region"]
    n_ants = data["n_ants"]
    n_iterations = data["n_iterations"]
    alpha = data["alpha"]
    beta = data["beta"]

    cities_data = load_cities("data/cities.yaml")
    cities = cities_data["cities"][region]

    cities_list = [(city["name"], city["lat"], city["lon"]) for city in cities]
    distances = np.zeros((len(cities_list), len(cities_list)))
    for i, (_, lat1, lon1) in enumerate(cities_list):
        for j, (_, lat2, lon2) in enumerate(cities_list):
            if i != j:
                distances[i][j] = great_circle((lat1, lon1), (lat2, lon2)).kilometers

    ant_colony = AntColony(distances, n_ants, n_iterations, alpha=alpha, beta=beta)
    shortest_path = ant_colony.run()

    fig = go.Figure()

    for city in cities_list:
        fig.add_trace(
            go.Scattergeo(
                lon=[city[2]],
                lat=[city[1]],
                text=city[0],
                mode="markers",
                marker=dict(size=8),
            )
        )

    path_cords = []
    for start, end in shortest_path[0]:
        lat1, lon1 = cities_list[start][1], cities_list[start][2]
        lat2, lon2 = cities_list[end][1], cities_list[end][2]
        path_cords.extend([(lon1, lat1), (lon2, lat2), (None, None)])

    path_lon, path_lat = zip(*path_cords)
    fig.add_trace(
        go.Scattergeo(
            lon=path_lon,
            lat=path_lat,
            mode="lines",
            line=dict(width=2, color="blue"),
            opacity=0.8,
        )
    )

    fig.update_layout(
        title=f"Shortest Path by Ant Colony Optimization for {region}",
        showlegend=False,
        geo=dict(
            scope=region.lower() if region.lower() != "poland" else "europe",
            projection_type="mercator",
            showland=True,
        ),
    )

    total_distance = sum(distances[i][j] for i, j in shortest_path[0])

    fig_dict = fig.to_dict()
    fig_dict["total_distance"] = total_distance
    response = json.dumps(fig_dict)

    return response


@app.route("/shutdown")
def shutdown():
    """
    shutdown
    """
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    app.run(debug=True)
