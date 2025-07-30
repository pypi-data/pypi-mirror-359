import folium
import requests
import webbrowser
import tempfile
import os
import json
from .weather import get_weather

class GeoMap:
    def __init__(self):
        self._map = None
        self._has_center = False

    def _get_coordinates(self, place_name):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place_name, "format": "json", "limit": 1}
        response = requests.get(url, params=params, headers={"User-Agent": "simplegeomap-app"})
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data['lat']), float(data['lon'])
        else:
            raise Exception(f"Place '{place_name}' not found.")

    def _init_map_if_needed(self, location):
        if not self._has_center:
            self._map = folium.Map(location=location, zoom_start=5)
            self._has_center = True

    def _center_on_path(self, coordinates):
        """
        Center the map on a path and adjust zoom level.
        """
        if not self._map:
            return
            
        # Get the bounding box of the path
        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]
        
        # Calculate center
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Calculate zoom level based on path length
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        range_sum = lat_range + lon_range
        
        # Adjust zoom based on path length
        if range_sum < 0.1:  # Very short path
            zoom = 12
        elif range_sum < 1:   # Short path
            zoom = 9
        elif range_sum < 5:   # Medium path
            zoom = 7
        else:                # Long path
            zoom = 5
            
        # Update map center and zoom
        self._map.location = [center_lat, center_lon]
        self._map.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=[5, 5])

    def add_marker(self, place_name, popup=None):
        lat, lon = self._get_coordinates(place_name)
        w = get_weather(place_name)
        self._init_map_if_needed([lat, lon])
        popup_text = place_name + "\n" + w
        folium.Marker([lat, lon], popup=popup_text, tooltip=place_name).add_to(self._map)

    def add_circle(self, place_name, radius=5000, color='blue', popup="Area"):
        lat, lon = self._get_coordinates(place_name)
        self._init_map_if_needed([lat, lon])
        folium.Circle([lat, lon], radius=radius, color=color, fill=True, popup=popup).add_to(self._map)

    def add_custom_icon_marker(self, place_name, icon_url, icon_size=(30, 30), popup="Custom Icon"):
        lat, lon = self._get_coordinates(place_name)
        self._init_map_if_needed([lat, lon])
        icon = folium.CustomIcon(icon_url, icon_size=icon_size)
        folium.Marker([lat, lon], icon=icon, popup=popup).add_to(self._map)
    def add_path(self, start_place, end_place, color='blue', weight=5, popup=None):
        lat1, lon1 = self._get_coordinates(start_place)
        lat2, lon2 = self._get_coordinates(end_place)
        self._init_map_if_needed([(lat1 + lat2) / 2, (lon1 + lon2) / 2])
        folium.PolyLine([(lat1, lon1), (lat2, lon2)], color=color, weight=weight, popup=popup).add_to(self._map)
    
    def _get_shortest_path_coordinates(self, start_place, end_place):
        # Get coordinates for both places
        start_lat, start_lon = self._get_coordinates(start_place)
        end_lat, end_lon = self._get_coordinates(end_place)
        
        # Use OSRM API to get shortest path
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            "steps": "false",
            "geometries": "geojson",
            "overview": "full"
        }
        
        response = requests.get(url, params=params, headers={"User-Agent": "simplegeomap-app"})
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok':
                # Convert coordinates from [lon, lat] to [lat, lon] format
                coordinates = data['routes'][0]['geometry']['coordinates']
                return [(lat, lon) for lon, lat in coordinates], data['routes'][0]['distance'] / 1000
        return [(start_lat, start_lon), (end_lat, end_lon)], 0

    def get_distance(self, start_place, end_place):

        _, distance = self._get_shortest_path_coordinates(start_place, end_place)
        return distance

    def add_shortest_path(self, start_place, end_place, color='blue', weight=5, popup=None):
        coordinates, distance = self._get_shortest_path_coordinates(start_place, end_place)
        if coordinates:
            # Initialize map if needed and center it on the path
            self._init_map_if_needed(coordinates[0])
            folium.PolyLine(coordinates, color=color, weight=weight, popup=popup).add_to(self._map)
            self._center_on_path(coordinates)
            
            # Add markers for start and end points
            folium.Marker(coordinates[0], popup=f"Start: {start_place}", icon=folium.Icon(color='green')).add_to(self._map)
            folium.Marker(coordinates[-1], popup=f"End: {end_place}", icon=folium.Icon(color='red')).add_to(self._map)
            
            # Add distance information to the popup
            if popup:
                popup = f"{popup} (Distance: {distance:.1f} km)"
            else:
                popup = f"Distance: {distance:.1f} km"
            
            # Add a popup marker showing the distance
            folium.Marker(
                coordinates[int(len(coordinates)/2)],  # Center of the path
                popup=popup,
                icon=folium.Icon(color='purple', icon='info-sign')
            ).add_to(self._map)

    def save(self, filepath="my_map.html"):
        if self._map:
            self._map.save(filepath)
        else:
            raise Exception("Map is empty. Add at least one place first.")

    def show(self):
        if self._map:
            tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
            self._map.save(tmp.name)
            webbrowser.open('file://' + os.path.realpath(tmp.name))
        else:
            raise Exception("Map is empty. Add at least one place first.")
