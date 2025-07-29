from .api_client import APIClient
import mcp.types as types
import json
from typing import Optional
api_client = APIClient()


def test_api_connection():
    
    try:
        authenticated =api_client.authenticate()
        if authenticated:
            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Successfully authenticated with API!\nBearer token obtained and ready for API calls.\nServer URL: {api_client.url}"
                )]
        else:
            return [types.TextContent(
                        type="text", 
                        text="❌ Failed to authenticate with API. Please check your credentials."
                    )]
    except Exception as error:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(error)}"
            )
        ]
        





def get_items(endpoint: str, expand: str| None, filter :str| None, select: str| None):
    try:
        if not endpoint:
            raise ValueError("Endpoint is required")
        item_data = api_client.get_items(
                endpoint, expand, filter, select
            )
        return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved items from {endpoint}:\n{json.dumps(item_data, indent=2)}"
                )
            ]
    
    except Exception as error:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(error)}"
            )
        ]


def api_create_item(endpoint:str, item_data:dict):
    try:
        if not endpoint:
            raise ValueError("Endpoint is required")
        if not item_data:
            raise ValueError("Item data is required")
        result = api_client.create_item(endpoint, item_data)
        return [
                types.TextContent(
                    type="text",
                    text=f"Successfully created item at {endpoint}:\n{json.dumps(result, indent=2)}"
                )
            ]
    except Exception as error:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(error)}"
            )
        ]


