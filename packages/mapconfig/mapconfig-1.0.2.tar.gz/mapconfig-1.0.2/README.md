# MapConfig

MapConfig is a simple, lightweight Python library for creating beautiful interactive maps using only place names (for example, "New Delhi", "Paris", "Tokyo") without needing to know coordinates.

It uses OpenStreetMap's Nominatim API to fetch coordinates and Folium to render maps.


## ⭐ Features

- 🔥 Add simple markers with just a place name
- 📍 Add circles to highlight areas
- 🖼️ Add custom icon markers
- 💨 Automatically center and display in the browser (no saving needed)
- 🌐 Show directly in a popup browser tab or export as HTML
- 🛣️ Add paths between two places
- 🗺️ Show shortest path between two places
- 🌤️ Add weather information to markers
- 🚀 More coming soon..

---

## 🚀 Available Function 

```python
1. add_marker(place_name, popup=None)
2. add_circle(place_name, radius=5000, color='blue', popup="Area")
3. add_custom_icon_marker(place_name, icon_url, icon_size=(30, 30), popup="Custom Icon")
4. add_path(start_place, end_place, color='blue', weight=5, popup=None)
5. add_shortest_path(start_place, end_place, color='blue', weight=5, popup=None)
6. get_distance(start_place, end_place)
7. show()
8. save(filepath="my_map.html")
```

## Example
```python
from mapconfig import GeoMap

m = GeoMap()
m.add_marker("New Delhi", popup="Capital City") # will also display weather information
m.add_circle("Hyderabad", radius=10000, color="green", popup="Cyber Hub")
m.add_custom_icon_marker("Chennai", icon_url="https://cdn-icons-png.flaticon.com/512/684/684908.png", popup="Beach City")
m.add_path("New Delhi", "Hyderabad", color="blue", weight=3, popup="Path from New Delhi to Hyderabad")
m.add_shortest_path("New Delhi", "Hyderabad", color="blue", weight=3, popup="Shortest path from New Delhi to Hyderabad")
m.show()
```