# app/geo_utils.py

import geocoder

def get_coordinates():
    """
    Returns the approximate latitude and longitude of the current user 
    based on their public IP address using geocoder.
    
    Returns:
        tuple or None: (latitude, longitude) if successful, None otherwise
    """
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            lat, lon = g.latlng
            return lat, lon
        else:
            print("⚠️ Could not retrieve location.")
            return None
    except Exception as e:
        print(f"[Geo Error] Failed to get coordinates: {e}")
        return None
