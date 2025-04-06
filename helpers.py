import re
from jinja2 import Template
import pandas as pd
import chromadb

chroma_client = chromadb.PersistentClient(
    "oof_db",
)

collection = chroma_client.create_collection(
    name="plants",
    get_or_create=True,
)


def extract_urls(text):
    """Extract URLs from a given text."""
    if pd.isna(text):
        return None
    # Regular expression to match URLs
    urls = re.findall(r"https?://[^\s,]+", text)
    return urls if urls else None


def render_plants_template(df: pd.DataFrame) -> list:
    """Render the plant details as an HTML template for each plant in the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing plant data.

    Returns
    -------
    list
        A list of rendered HTML strings for each plant.
    """
    rendered_plants = []
    template = template = Template(
        """
    <div class="mb-4 p-4 bg-white rounded shadow">
        <h1>
            {{ plant_name }} 
            <span class="bg-green-100 text-green-800 text-sm font-semibold px-2.5 py-0.5 rounded">
                similarity: {{ similarity }}
            </span>
        </h1>
        <p><strong>Common Names:</strong> {{ common_names }}</p>
        <p><strong>Family:</strong> {{ family }}</p>
        <p><strong>Origin:</strong> {{ origin }}</p>
        <p><strong>Edible Parts:</strong> {{ edible_parts }}</p>
        <p><strong>Type of Plant:</strong> {{ type_of_plant }}</p>
        <p><strong>Foliage:</strong> {{ foliage }}</p>
        <p><strong>Max Height:</strong> {{ max_height }}</p>
        <p><strong>Environmental Attributes:</strong> {{ environmental_attributes }}</p>
        <p><strong>Ideal Soil:</strong> {{ ideal_soil }}</p>
        <p><strong>Ideal Sun Exposure:</strong> {{ ideal_sun_exposure }}</p>
        <p><strong>Water Preferences:</strong> {{ water_preferences }}</p>
        <p><strong>Pollination:</strong> {{ pollination }}</p>
        {% if plant_images %}
            <p><strong>Plant Images:</strong></p>
            <div class="flex space-x-4">
                {% for url in plant_images %}
                    <img src="{{ url }}" alt="Plant Image" class="rounded shadow" style="width: 300px;">
                {% endfor %}
            </div>
        {% endif %}
    </div>
    """
    )
    for _, row in df.iterrows():
        plant_images = extract_urls(row["ADULTTREE"]) if "ADULTTREE" in row else None
        rendered_plants.append(
            template.render(
                plant_name=row["LATIN NAME"],
                similarity=round(row["similarity"], 2) if "similarity" in row else None,
                common_names=row["COMMON NAMES"],
                family=row["Family"],
                origin=row["ORIGIN"],
                edible_parts=row["EDIBLE PARTS"],
                type_of_plant=row["TYPE OF PLANTS"],
                foliage=row["FOLIAGE"],
                max_height=row["MAX. HEIGHT"],
                environmental_attributes=row["ENVIRONMENTAL ATTRIBUTES"],
                ideal_soil=row["IDEAL SOIL"],
                ideal_sun_exposure=row["IDEAL SUN EXPOSURE"],
                water_preferences=row["WATER PREFERENCES"],
                pollination=row["POLLINATION"],
                plant_images=plant_images,
            )
        )
    return rendered_plants


def get_chroma_recommendation(prompt_list: list[str], amount_recommendations=1):
    """Get recommendations from the Chroma vector database.

    Parameters
    ----------
    prompt_list : list[str]
        List of prompts to query the vector database.
    amount_recommendations : int
        Number of recommendations to retrieve.

    Returns
    -------
    tuple
        A tuple containing two lists: plant IDs and their corresponding similarities to the query.

    """
    response = collection.query(
        query_texts=prompt_list,
        n_results=amount_recommendations,
    )
    documents = response.get("documents")[0]
    metadatas = response.get("metadatas")[0]
    similarities = response.get("distances")[0]
    plant_id_list = [metadatas[i].get("plant_id") for i in range(len(documents))]
    similarities_list = [similarities[i] for i in range(len(documents))]
    return plant_id_list, similarities_list
