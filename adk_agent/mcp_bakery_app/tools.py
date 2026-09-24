import os
from pathlib import Path
import dotenv
import google.auth
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams 

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp" 
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 

def _load_env():
    _current_dir = Path(__file__).resolve().parent
    for p in [_current_dir / '.env', _current_dir.parent / '.env', _current_dir.parent.parent / '.env']:
        if p.exists():
            dotenv.load_dotenv(p)
    dotenv.load_dotenv()

def get_maps_mcp_toolset():
    _load_env()
    maps_api_key = os.getenv('MAPS_API_KEY', '')
    if not maps_api_key or maps_api_key == 'no_api_found':
        print("[Warning] MAPS_API_KEY not configured. Maps MCP toolset skipped.")
        return None
    
    try:
        tools = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MAPS_MCP_URL,
                headers={    
                    "X-Goog-Api-Key": maps_api_key
                },
                timeout=30.0,          
                sse_read_timeout=300.0
            )
        )
        print("MCP Toolset configured for Google Maps Streamable HTTP connection.")
        return tools
    except Exception as e:
        print(f"[Warning] Could not initialize Maps MCP toolset: {e}")
        return None


def get_bigquery_mcp_toolset():   
    _load_env()
    try:
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        oauth_token = credentials.token
        resolved_project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')
            
        HEADERS_WITH_OAUTH = {
            "Authorization": f"Bearer {oauth_token}",
            "x-goog-user-project": resolved_project_id
        }

        tools = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BIGQUERY_MCP_URL,
                headers=HEADERS_WITH_OAUTH,
                timeout=30.0,          
                sse_read_timeout=300.0
            )
        )
        print("MCP Toolset configured for BigQuery Streamable HTTP connection.")
        return tools
    except Exception as e:
        print(f"[Warning] Could not initialize BigQuery MCP toolset (ensure 'gcloud auth application-default login' is run): {e}")
        return None
