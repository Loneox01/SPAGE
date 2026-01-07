import uuid

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def change_background(red: int = 0, green: int = 0, blue: int = 0):
    """
    Changes the website's background color using RGB values.
    
    Args:
        red: The red intensity (0-255)
        green: The green intensity (0-255)
        blue: The blue intensity (0-255)
    """

    red = max(0, min(255, red))
    green = max(0, min(255, green))
    blue = max(0, min(255, blue))

    return {
        "status": "success",
        "action": "change_background",
        "payload": {
            "r": red,
            "g": green,
            "b": blue
        },
        "error": None
    }

def spawn_text(content: str, color: str = "white", font: str = "sans-serif", font_size: int = 20, x: int = 50, y: int = 40, z: int = 1):
    """
    Spawns a new text element onto the website background.

    Args:
        content: (REQUIRED) The text content to be spawned
        color: Text color as a string
        font: Text font
        font_size: Font size in px
        x: Horizontal position (0-100 percentage of screen width)
        y: Vertical position (0-100 percentage of screen height)
        z: Integer index for relative depth (0-100)
    """

    x = max(0, min(100, x))
    y = max(0, min(100, y))
    z = max(0, min(100, z))

    font_size = max(8, min(200, font_size))  # font size restricted to 8 <= fs <= 200

    return {
        "status": "success",
        "action": "spawn_text",
        "payload": {
            "id": str(uuid.uuid4())[:8],
            "content": content,
            "color": color,
            "font": font,
            "font_size": str(font_size) + "px",
            "x": str(x) + "%",
            "y": str(y) + "%",
            "z_index": z
        },
        "error": None
    }

def edit_text(element_id: str, content: str = None, color: str = None, font: str = None, font_size: int = None, x: int = None, y: int = None, z: int = None):
    """
    Edits the existing text element with the corresponding id. Only provided fields will be updated.

    Args:
        element_id: (REQUIRED) The string id of the text to be edited
        content: New text content
        color: New text color
        font: New text font
        font_size: New font size in px (clamped 8-200)
        x: New horizontal position (0-100)%
        y: New vertical position (0-100)%
        z: New integer index for relative depth (0-100)
    """

    raw_payload = {
        "id": element_id,
        "content": content,
        "color": color,
        "font": font,
        "font_size": f"{max(8, min(200, font_size))}px" if font_size is not None else None,
        "x": f"{max(0, min(100, x))}%" if x is not None else None,
        "y": f"{max(0, min(100, y))}%" if y is not None else None,
        "z_index": max(0, min(100, z)) if z is not None else None
    }

    # strip None values, send changes
    payload = {k: v for k, v in raw_payload.items() if v is not None}

    return {
        "status": "success",
        "action": "edit_text",
        "payload": payload,
        "error": None
    }

def spawn_image(url: str = None, query: str = None, x: int = 50, y: int = 60, width: int = 300, z: int = 1):
    """
    Spawns a new image with the provided url onto the the website background.

    IMPORTANT: Either a 'url' XOR a 'query' MUST be provided.
    - If a direct link already exists, use it
    - Provide a query if no direct link exists
    
    Args:
        url: The url of the image as a string
        query: A description of the image
        x: Horizontal position (0-100 percentage of screen width)
        y: Vertical position (0-100 percentage of screen height)
        width: Width of the image in px
        z: Integer index for relative depth

    """

    if not url and not query:
        return {
            "status": "error",
            "action": "none",
            "payload": None,
            "error": "BAD_CALL"
        }
    
    if not url:
        url = get_image_url(query)

    if not url or not is_valid_image(url):
        return {
            "status": "error",
            "action": "none",
            "payload": None,
            "error": "IMAGE_NOT_FOUND"
        }

    x = max(0, min(100, x))
    y = max(0, min(100, y))
    z = max(0, min(100, z))

    width = max(50, min(1200, width))

    return {
        "status": "success",
        "action": "spawn_image",
        "payload": {
            "id": str(uuid.uuid4())[:8],
            "url": url,
            "x": str(x) + "%",
            "y": str(y) + "%",
            "width": str(width) + "px",
            "z_index": z
        },
        "error": None
    }

def edit_image(element_id: str, url: str = None, query: str = None, x: int = None, y: int = None, width: int = None, z: int = None):
    """
    Edits the existing image element with the corresponding id. Only provided fields will be updated.

    IMPORTANT: Do not provide BOTH a url AND a query

    Args:
        element_id: (REQUIRED) The string id of the text to be edited
        url: New url
        query: Description of new image
        x: New horizontal position (0-100)%
        y: New vertical position (0-100)%
        width: New width in px
        z: New integer index for relative depth (0-100)
    """

    if query and not url:
        url = get_image_url(query)
        if not url or not is_valid_image(url):
            return {
                "status": "error",
                "action": "none",
                "payload": None,
                "error": "IMAGE_NOT_FOUND"
            }
    else:
        if url and not is_valid_image(url):
            return {
                "status": "error",
                "action": "none",
                "payload": None,
                "error": "IMAGE_NOT_FOUND"
            }
        
    raw_payload = {
        "id": element_id,
        "url": url,
        "x": f"{max(0, min(100, x))}%" if x is not None else None,
        "y": f"{max(0, min(100, y))}%" if y is not None else None,
        "width": f"{max(50, min(1200, width))}" + "px" if width is not None else None,
        "z_index": max(0, min(100, z)) if z is not None else None
    }

    # strip None values, send changes
    payload = {k: v for k, v in raw_payload.items() if v is not None}

    return {
        "status": "success",
        "action": "edit_image",
        "payload": payload,
        "error": None
    }

def delete_elements(element_ids: list[str]):
    """
    Deletes specific text elements from the screen by their IDs.

    Args:
        element_ids: (REQUIRED) A list of string IDs of the elements to be removed.
    """
    return {
        "status": "success",
        "action": "delete_elements",
        "payload": {
            "ids": element_ids
        },
        "error": None
    }

def unsupported_request():
    """
    Handles ALL requests that do not match any of the other tools.
    """
    return {
        "status": "error",
        "action": "none",
        "payload": None,
        "error": "UNSUPPORTED_COMMAND"
    }

ALL_TOOLS = [change_background, edit_text, spawn_text, spawn_image, edit_image, delete_elements, unsupported_request]

# Not TOOLS

def get_image_url(query: str):
    print("get_image_url called with")
    print(f"query: {query}")
    client_id = os.getenv("UNSPLASH_ACCESS_KEY")
    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": query,
        "client_id": client_id,
        "per_page": 1,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        # returns url
        return data['results'][0]['urls']['regular']
    except Exception:
        return None
    
def is_valid_image(url: str) -> bool:
    try:
        response = requests.head(url, allow_redirects=True, timeout=2)
        
        if response.status_code != 200:
            return False
            
        # Check content type, it should look like 'image/jpeg', 'image/png', 'image/webp'
        content_type = response.headers.get("Content-Type", "")
        
        if content_type.startswith("image/"):
            return True
            
        return False

    except Exception as e:
        # If there's a timeout or connection error, assume invalid
        return False