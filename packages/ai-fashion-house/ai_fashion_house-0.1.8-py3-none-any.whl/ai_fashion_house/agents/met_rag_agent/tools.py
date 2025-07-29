import asyncio
import base64
import io
import logging
import os
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

import google.genai.types as types
import pandas as pd
from PIL import Image
from dotenv import load_dotenv, find_dotenv
from google.adk.tools import ToolContext
from google.cloud import bigquery, storage
from rich.logging import RichHandler

# --- Setup Rich Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("FashionRAG")

# --- Load Environment Variables ---
load_dotenv(find_dotenv())


GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
BIGQUERY_EMBEDDINGS_MODEL_ID = os.getenv("BIGQUERY_EMBEDDINGS_MODEL_ID")
BIGQUERY_REGION= os.getenv("BIGQUERY_REGION", "US")
BIGQUERY_VECTOR_INDEX_ID = os.getenv("BIGQUERY_VECTOR_INDEX_ID")
BIGQUERY_TABLE_ID = os.getenv("BIGQUERY_TABLE_ID")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Initialize Clients ---
bq_client = bigquery.Client(project=GOOGLE_PROJECT_ID, location=BIGQUERY_REGION)
gcs_client = storage.Client(project=GOOGLE_PROJECT_ID)


def run_bigquery(sql: str) -> pd.DataFrame:
    """
    Executes a BigQuery SQL query and returns the results as a DataFrame.

    Args:
        sql (str): SQL query to execute.

    Returns:
        pd.DataFrame: Results from the executed query.

    Raises:
        RuntimeError: If the query execution fails.
    """
    try:
        job = bq_client.query(sql)
        result = job.result()
        logger.info(f"[✅] Query succeeded: Job ID {job.job_id}")
        return result.to_dataframe()
    except Exception as e:
        logger.exception(f"[❌] Query failed: {e}")
        raise


def search_fashion_embeddings(query: str, top_k: int = 6, search_fraction: float = 0.01) -> pd.DataFrame:
    """
    Performs a vector similarity search using a fashion-related query on a BigQuery embedding table.

    Args:
        query (str): Text to embed and search against the vector database.
        top_k (int, optional): Number of top results to return. Defaults to 6.
        search_fraction (float, optional): Fraction of the vector index to search. Defaults to 0.01.

    Returns:
        pd.DataFrame: A DataFrame with matching content, distances, and image URLs.
    """
    sql = f"""
    SELECT 
    base.object_id,
    base.object_name,
    base.object_begin_date,
    base.object_end_date,
    base.content, 
    base.gcs_url, 
    query.query, 
    distance
    FROM VECTOR_SEARCH(
        TABLE `{GOOGLE_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}_embeddings`,
        'text_embedding',
        (
            SELECT text_embedding, content AS query
            FROM ML.GENERATE_TEXT_EMBEDDING(
                MODEL `{GOOGLE_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_EMBEDDINGS_MODEL_ID}`,
                (SELECT "{query}" AS content)
            )
        ),
        top_k => {top_k},
        OPTIONS => '{{"fraction_lists_to_search": {search_fraction}}}'
    )
    """
    return run_bigquery(sql)


def pil_image_to_base64(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Converts a Pillow image to a base64-encoded string.

    Args:
        image (PIL.Image.Image): The image to encode.
        format (str): Format for encoding (e.g., "PNG", "JPEG"). Defaults to "PNG".

    Returns:
        str: Base64-encoded image string (without data URI prefix).
    """
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    encoded_bytes = base64.b64encode(img_bytes)
    return encoded_bytes

def pil_image_to_png_bytes(image: Image.Image) -> bytes:
    """
    Converts a Pillow image to raw PNG bytes in memory.

    Args:
        image (PIL.Image.Image): The image to convert.

    Returns:
        bytes: PNG-encoded image bytes.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()

async def retrieve_met_images(user_query: str, top_k: int = 6, search_fraction: float = 0.01, tool_context: ToolContext = None) -> dict:
    """
    Orchestrates the full RAG pipeline: refines the user query, retrieves similar embeddings,
    and returns a list of matching GCS image URLs.

    Also generates a moodboard of the top results.

    Args:
        user_query (str): Initial query string describing the desired fashion style.
        top_k (int, optional): Number of top image results to return. Defaults to 6.
        search_fraction (float, optional): Search scope for approximate vector match. Defaults to 0.01.
        tool_context (ToolContext, optional): Context for tool execution, if needed.

    Returns:
        Optional[List[str]]: A list of GCS URLs to matching images, or None if no matches found.
    """
    # refined_query = enhance_fashion_prompt(user_query)
    # logger.info(f"[✨] Enhanced Query: {refined_query}")
    try:
        results = search_fashion_embeddings(user_query , top_k=top_k, search_fraction=search_fraction)
        if results.empty:
            logger.warning("[⚠️] No matches found.")
            return None

        logger.info(f"[✅] Retrieved {len(results)} matching results.")

        image_urls = results['gcs_url'].dropna().tolist()
        moodboard_image = create_moodboard(image_urls)
        if tool_context:
            # Save moodboard to GCS if tool context is provided
            moodboard_artifact_part = types.Part.from_bytes(mime_type="image/png",data=pil_image_to_png_bytes(moodboard_image))
            await tool_context.save_artifact("moodboard.png", moodboard_artifact_part)
            met_rag_results = types.Part.from_bytes(
                mime_type="text/csv",
                data=results.to_csv(index=False).encode('utf-8')
            )
            await tool_context.save_artifact("met_rag_results.csv", met_rag_results)


        # Save moodboard locally if no tool context is provided
        output_folder = Path(os.getenv("OUTPUT_FOLDER", "outputs"))
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / "moodboard.png"
        moodboard_image.save(output_file)

        logger.info(f"[🖼️] Moodboard saved @ {output_file}")
        return {
            "status": "success",
            "result": image_urls,
        }
    except Exception as e:
        logger.error(f"[❌] Error during retrieval: {e}")
        return {
            "status": "error",
            "message": str(e),
        }



def load_gcs_image(gs_url: str) -> Optional[Image.Image]:
    """
    Downloads and loads an image stored in Google Cloud Storage.

    Args:
        gs_url (str): GCS path in the form `gs://bucket_name/path/to/image`.

    Returns:
        Optional[PIL.Image.Image]: The downloaded image as a PIL object, or None if loading fails.
    """
    try:
        parsed = urlparse(gs_url)
        bucket = gcs_client.bucket(parsed.netloc)
        blob = bucket.blob(parsed.path.lstrip("/"))
        img_bytes = blob.download_as_bytes()
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        logger.warning(f"[⚠️] Failed to load {gs_url}: {e}")
        return None


def create_moodboard(
    image_urls: List[str],
    thumb_size: tuple = (300, 300),
    padding: int = 10,
    margin: int = 20,
    columns: int = 3,
    bg_color: str = "white"
) -> Image.Image:
    """
    Creates a moodboard from GCS image URLs using Pillow without cropping the images.
    Resizes each image to fit within the thumbnail box while maintaining aspect ratio.
    Images are arranged in a grid, centered in their cells, with consistent padding and outer margin.

    Args:
        image_urls (List[str]): List of GCS image URLs (gs://...).
        thumb_size (tuple): Maximum width and height of each thumbnail.
        padding (int): Space between images.
        margin (int): Outer space around the moodboard.
        columns (int): Number of columns in the grid.
        bg_color (str): Background color.

    Returns:
        PIL.Image.Image: The moodboard image assembled in memory.
    """
    if not image_urls:
        raise ValueError("No images provided for moodboard.")

    thumbs = []
    for i, url in enumerate(image_urls):
        img = load_gcs_image(url)
        if img:
            #img.save(f"moodboard_{i}.png")
            img.thumbnail(thumb_size, Image.LANCZOS)
            thumb = Image.new("RGB", thumb_size, color=bg_color)
            offset_x = (thumb_size[0] - img.width) // 2
            offset_y = (thumb_size[1] - img.height) // 2
            thumb.paste(img, (offset_x, offset_y))
            thumbs.append(thumb)
        else:
            logger.warning(f"[⚠️] Skipping unavailable image: {url}")

    if not thumbs:
        raise ValueError("No valid images could be loaded.")

    rows = (len(thumbs) + columns - 1) // columns
    board_width = columns * thumb_size[0] + (columns - 1) * padding + 2 * margin
    board_height = rows * thumb_size[1] + (rows - 1) * padding + 2 * margin
    moodboard = Image.new("RGB", (board_width, board_height), color=bg_color)

    for idx, thumb in enumerate(thumbs):
        row, col = divmod(idx, columns)
        x = margin + col * (thumb_size[0] + padding)
        y = margin + row * (thumb_size[1] + padding)
        moodboard.paste(thumb, (x, y))

    logger.info(f"[🖼️] Moodboard created with {len(thumbs)} images (symmetrically aligned with margin)")
    return moodboard


def run_retrieve_met_images_sync(
    user_query: str,
    top_k: int = 5,
    search_fraction: float = 0.01,
    tool_context: Optional[ToolContext] = None
) -> Optional[List[str]]:
    """
    Synchronous wrapper for the fashion image retrieval function.

    Args:
        user_query (str): User's fashion-related query.
        top_k (int): Number of top results to return.
        search_fraction (float): Fraction of the vector index to search.
        tool_context (Optional[ToolContext]): Context for tool execution, if needed.

    Returns:
        Optional[List[str]]: List of GCS URLs to retrieved images, or None if no matches found.
    """
    return asyncio.run(
        retrieve_met_images(
            user_query=user_query,
            top_k=top_k,
            search_fraction=search_fraction,
            tool_context=tool_context
        )
    )

# --- Entry Point ---
if __name__ == '__main__':
    logger.info("[📂] Listing tables in MET dataset...")
    tables = bq_client.list_tables("bigquery-public-data.the_met")
    for table in tables:
        logger.info(f"• {table.project}.{table.bigquery_dataset_id}.{table.table_id}")

    query = "A pink Victorian dress with lace and floral patterns, suitable for a royal ball in the 1800s."
    image_results = run_retrieve_met_images_sync(
        user_query=query,
        top_k=5,
        search_fraction=0.01
    )
    if image_results:
        logger.info(f"[📸] Retrieved image URLs:\n{image_results}")
