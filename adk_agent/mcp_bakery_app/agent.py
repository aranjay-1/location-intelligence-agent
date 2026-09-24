import os
from pathlib import Path
import dotenv

# Load .env from multiple potential locations (current dir, app dir, parent dir)
_current_dir = Path(__file__).resolve().parent
for p in [_current_dir / '.env', _current_dir.parent / '.env', _current_dir.parent.parent / '.env']:
    if p.exists():
        dotenv.load_dotenv(p)
dotenv.load_dotenv()

# If GEMINI_API_KEY is set and VERTEXAI is not explicitly forced, use Gemini API mode (No GCP billing required)
if os.getenv('GEMINI_API_KEY') and os.getenv('GOOGLE_GENAI_USE_VERTEXAI') != '1':
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '0'

from mcp_bakery_app import tools
from google.adk.agents import LlmAgent

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "endless-gasket-495808-d3")
MODEL_NAME = os.getenv("ADK_MODEL", "gemini-3.5-flash")

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()
active_tools = [t for t in [maps_toolset, bigquery_toolset] if t is not None]

root_agent = LlmAgent(
    model=MODEL_NAME,
    name='root_agent',
    instruction=f"""
                You are an advanced Location Intelligence & Business Advisory Agent capable of analyzing locations, cities, states, and regions all across the world.

                Help the user answer questions by combining real-world geospatial intelligence, demographic context, and enterprise datasets:

                1.  **Worldwide Location & State Intelligence:**
                    - Support inquiries for any state, province, city, neighborhood, or country globally (e.g., Uttar Pradesh, California, Tokyo, London, etc.).
                    - When a user asks about or mentions any state, region, or city worldwide, provide rich location intelligence: geography, key commercial hubs, population density, market opportunities, and strategic advice.
                    - Always utilize the **Maps Toolset** to perform real-world spatial searches: finding points of interest, competitors, retail locations, geocoding, and calculating travel routes anywhere across the globe.
                    - Include clickable markdown hyperlinks to interactive Google Maps (e.g., `https://www.google.com/maps/search/?api=1&query=...`) for locations and businesses referenced.

                2.  **BigQuery Toolset (Benchmark & Demo Datasets):**
                    - When analyzing the Los Angeles / California bakery demo scenario, access demographic foot traffic, competitor pricing, and historical sales in the `mcp_bakery` dataset within project: {PROJECT_ID}.
                    - For all other global locations, states, and markets outside the LA bakery dataset, seamlessly leverage the Google Maps tools and your knowledge to evaluate foot traffic, competitor density, and commercial viability.

                Always deliver clear, structured, and insightful location intelligence for any state or place around the world.
            """,
    tools=active_tools
)

