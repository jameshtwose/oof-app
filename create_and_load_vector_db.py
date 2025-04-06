import chromadb
import json
import pandas as pd

# chroma_client = chromadb.Client()
chroma_client = chromadb.PersistentClient(
    "oof_db",
)

# Check if the collection already exists
if "plants" in [col.name for col in chroma_client.list_collections()]:
    collection = chroma_client.get_collection(name="plants")
else:
    collection = chroma_client.create_collection(name="plants")
# LATIN NAME,COMMON NAMES,Family,ORIGIN,ADULTTREE,EDIBLE PARTS PICTURES,EDIBLE PARTS,TYPE OF PLANTS,FOLIAGE,MAX. HEIGHT,RUSTICITY ZONES USDA,ENVIRONMENTAL ATTRIBUTES,IDEAL SOIL,IDEAL SUN EXPOSURE,WATER PREFERENCES,POLLINATION,HEIGHT AT PLANTATION CM,DIAMETER AT PLANTATION CM,SOIL WHERE PLANTED,IDEAL WIND EXPOSURE,SOIL PREPARATION,HOLE DIAMETER CM,HOLE DEPTH CM,ADDITIONS TO SOIL,PLANTATION DATE,PLANTING PICTURES,ZONE LOCATION,WIND EXPOSURE WHERE PLANTED,MYCORRHIZAL,GRAFTED,ID
column_list = [
    "LATIN NAME",
    "COMMON NAMES",
    "Family",
    "ORIGIN",
    # "ADULTTREE",
    # "EDIBLE PARTS PICTURES",
    "EDIBLE PARTS",
    "TYPE OF PLANTS",
    "FOLIAGE",
    "MAX. HEIGHT",
    "RUSTICITY ZONES USDA",
    "ENVIRONMENTAL ATTRIBUTES",
    "IDEAL SOIL",
    "IDEAL SUN EXPOSURE",
    "WATER PREFERENCES",
    "POLLINATION",
    "HEIGHT AT PLANTATION CM",
    "DIAMETER AT PLANTATION CM",
    "SOIL WHERE PLANTED",
    "IDEAL WIND EXPOSURE",
    "SOIL PREPARATION",
    "HOLE DIAMETER CM",
    "HOLE DEPTH CM",
    "ADDITIONS TO SOIL",
    "PLANTATION DATE",
    # "PLANTING PICTURES",
    "ZONE LOCATION",
    "WIND EXPOSURE WHERE PLANTED",
    "MYCORRHIZAL",
    "GRAFTED",
    "ID"]
data = pd.read_csv("data/plants-2025-04-05.csv").assign(
    description=lambda x: x.apply(
        # join the columns into a single string
        lambda row: " ".join(
            [
                str(row[col])
                for col in column_list
                if col != "ID" and pd.notna(row[col])
            ]
        ),
        axis=1,
    )
).to_dict(orient="records")

collection.upsert(
    documents=[row["description"] for row in data],
    metadatas=[
        {
            "title": row["LATIN NAME"],
            "plant_id": row["ID"],
        }
        for row in data
    ],
    ids=[str(i) for i in range(len(data))],
)

# collection.delete_all()