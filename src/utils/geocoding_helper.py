from typing import Optional, Dict 
import requests
import time

from . import logger

class GeocodingHelper:
    """Helper class to handle geocoding requests using Nominatim API."""
    
    def __init__(self, user_agent: str = "DisasterDataAnalysis/1.0"):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = user_agent
    
    def get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location using Nominatim API."""
        if not location:
            return None
            
        logger.info(f"Fetching coordinates for: {location}")
        time.sleep(1.1)  # Maximum 1 request per second
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    'q': location,
                    'format': 'json',
                    'limit': 1,
                },
                headers={'User-Agent': self.user_agent}
            )
            response.raise_for_status()
            
            results = response.json()
            if not results:
                logger.warning(f"No coordinates found for: {location}")
                return None
                
            return {
                'latitude': float(results[0]['lat']),
                'longitude': float(results[0]['lon'])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {location}: {str(e)}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse API response for {location}: {str(e)}")
            return None
