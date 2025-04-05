from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
import os
import pandas as pd
import httpx
from datetime import date

from helpers import render_plants_template

app = FastAPI(
    title="Orchards of Flavour API",
    version="0.0.1",
    description="A simple API for requesting plants from the Orchards of Flavour.",
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")


df = pd.read_csv(
    "data/plants-2025-04-05.csv",
    encoding="utf-8",
)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint.

    Parameters
    ----------
    None

    Returns:
    -------
    dict
        A dictionary containing a welcome message.

    """
    return HTMLResponse(
        "<h2>Hi, this is a web UI for the orchards of flavour data.</h2>"
    )


@app.get("/home", tags=["Static"])
def get_index():
    """Serve the index.html file.

    Returns
    -------
    FileResponse
        The index.html file.
    """
    return FileResponse("index.html")


@app.get("/plants", tags=["Plants"])
def get_plants(
    query: str,
    return_type: str = "html",
):
    """Get plants based on the query.
    
    Parameters
    ----------
    query : str
        The query to search for plants.
    return_type : str
        The type of response to return. Can be "html" or "json".
        Defaults to "html".
    
    Returns
    -------
    HTMLResponse or JSONResponse
        The response containing the plants based on the query.
    
    """
    filtered_plants = df[
        df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    ]
    if filtered_plants.empty:
        if return_type == "html":
            return HTMLResponse(
                """
                <div class="mb-4 p-4 bg-white rounded shadow">
                    <h1>No plants found matching the requested query</h1>
                    <p>Try a different search term.</p>
                </div>
                """
            )
        elif return_type == "json":
            return HTTPException(
                status_code=404,
                detail="No plants found.",
            )
        else:
            return HTTPException(
                status_code=400,
                detail="Invalid return type. Must be 'html' or 'json'.",
            )
    if return_type == "html":
        plants_list = render_plants_template(filtered_plants)
        template = Template(
            """
            <div class="mb-4 p-4 bg-white rounded shadow">
                <h1>Plants matching '{{ query }}'</h1>
                <p>Found {{ plants|length }} plant(s).</p>
            </div>
            <div class="container">
                {% for plant in plants %}
                    {{ plant }}
                {% endfor %}
            </div>
            """
        )
        return HTMLResponse(
            template.render(
                query=query,
                plants=plants_list)
        )
    elif return_type == "json":
        return filtered_plants.astype(str).to_dict(orient="records")

    else:
        return HTTPException(
            status_code=400,
            detail="Invalid return type. Must be 'html' or 'json'.",
        )


@app.get("/plants/{plant_id}", tags=["Plants"])
def get_plant_by_id(
    plant_id: str,
    return_type: str = "html",
):
    """Get a plant by its ID.
    
    Parameters
    ----------
    plant_id : str
        The ID of the plant to search for.
    return_type : str
        The type of response to return. Can be "html" or "json".
        Defaults to "html".
    
    Returns
    -------
    HTMLResponse or JSONResponse
        The response containing the plant with the specified ID.
    
    """
    selected_plant = df[df["ID"] == int(plant_id)]
    if selected_plant.empty:
        return HTTPException(
            status_code=404,
            detail="Plant not found.",
        )
    if return_type == "html":
        plants_list = render_plants_template(selected_plant)
        return HTMLResponse(
            plants_list[0]
        )
    elif return_type == "json":
        return selected_plant.astype(str).to_dict(orient="records")

    else:
        return HTTPException(
            status_code=400,
            detail="Invalid return type. Must be 'html' or 'json'.",
        )