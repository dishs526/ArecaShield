# weather.py - Weather service class with all weather-related logic
import requests
from datetime import datetime

class WeatherService:
    def __init__(self):
        self.weather_descriptions = {
            0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
            45: 'Fog', 48: 'Freezing fog', 51: 'Light drizzle', 53: 'Moderate drizzle',
            55: 'Dense drizzle', 61: 'Light rain', 63: 'Moderate rain', 65: 'Heavy rain',
            71: 'Light snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
            95: 'Thunderstorm', 96: 'Thunderstorm with hail', 99: 'Thunderstorm with heavy hail'
        }
    
    def get_coordinates(self, city, state, country):
        """Get coordinates from location using geocoding APIs"""
        location_query = ', '.join(filter(None, [city, state, country]))
        
        # Try Nominatim first for geocoding
        try:
            nominatim_url = f"https://nominatim.openstreetmap.org/search?q={location_query}&format=json&addressdetails=1&limit=1"
            headers = {'User-Agent': 'ArecaShield/1.0'}
            geo_response = requests.get(nominatim_url, headers=headers, timeout=10)
            geo_data = geo_response.json()
            
            if geo_data:
                result = geo_data[0]
                latitude = float(result['lat'])
                longitude = float(result['lon'])
                full_location = f"{result.get('address', {}).get('city', city)}, {result.get('address', {}).get('state', state)}, {result.get('address', {}).get('country', country)}"
                return latitude, longitude, full_location
            else:
                raise Exception("Location not found in Nominatim")
                
        except:
            # Fallback to Open-Meteo geocoding
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_query}&count=1&language=en&format=json"
            geo_response = requests.get(geocoding_url, timeout=10)
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                raise ValueError('Location not found. Please check spelling and try again.')
            
            result = geo_data['results'][0]
            latitude = result['latitude']
            longitude = result['longitude']
            full_location = f"{result.get('name', city)}, {result.get('admin1', state)}, {result.get('country', country)}"
            
            return latitude, longitude, full_location
    
    def fetch_weather_data(self, latitude, longitude):
        """Fetch weather data from Open-Meteo API"""
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,precipitation,visibility,uv_index&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max,uv_index_max&timezone=auto&forecast_days=5"
        
        try:
            weather_response = requests.get(weather_url, timeout=10)
            weather_data = weather_response.json()
            
            if 'current' not in weather_data:
                raise ConnectionError('Weather data not available for this location')
            
            return weather_data
            
        except requests.exceptions.Timeout:
            raise TimeoutError('Request timeout. Please try again.')
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'Network error: {str(e)}')
    
    def process_weather_data(self, weather_data, location):
        """Process raw weather data into structured format"""
        current = weather_data['current']
        daily = weather_data['daily']
        
        # Prepare response data
        result_data = {
            'location': location,
            'current': {
                'temperature': current.get('temperature_2m'),
                'weather_code': current.get('weather_code'),
                'weather_description': self.weather_descriptions.get(current.get('weather_code', 0), 'Unknown'),
                'humidity': current.get('relative_humidity_2m'),
                'wind_speed': current.get('wind_speed_10m'),
                'precipitation': current.get('precipitation'),
                'visibility': current.get('visibility'),
                'uv_index': current.get('uv_index'),
                'timestamp': datetime.now().strftime('%I:%M %p IST, %A, %B %d, %Y')
            },
            'forecast': [],
            'arecanut_tips': self.generate_arecanut_tips(current, daily)
        }
        
        # Process 5-day forecast
        for i in range(5):
            forecast_day = {
                'date': daily['time'][i],
                'max_temp': daily['temperature_2m_max'][i],
                'min_temp': daily['temperature_2m_min'][i],
                'weather_code': daily['weather_code'][i],
                'weather_description': self.weather_descriptions.get(daily['weather_code'][i], 'Unknown'),
                'precipitation': daily['precipitation_sum'][i],
                'max_wind': daily['wind_speed_10m_max'][i],
                'max_uv': daily.get('uv_index_max', [None] * 5)[i]
            }
            result_data['forecast'].append(forecast_day)
        
        return result_data
    
    def generate_arecanut_tips(self, current, daily):
        """Generate specific tips for arecanut cultivation based on weather data"""
        tips = []
        
        temp = current.get('temperature_2m', 0)
        humidity = current.get('relative_humidity_2m', 0)
        precipitation = current.get('precipitation', 0)
        wind_speed = current.get('wind_speed_10m', 0)
        
        # Temperature-based tips
        if temp > 35:
            tips.append('🌡️ High temperature alert - Provide shade nets for young arecanut plants and increase irrigation frequency.')
        elif temp < 15:
            tips.append('❄️ Low temperature warning - Protect young plants from cold damage and reduce watering.')
        
        # Humidity-based tips
        if humidity > 80:
            tips.append('💧 High humidity detected - Watch for fungal diseases like leaf blight and stem rot. Ensure good drainage.')
        elif humidity < 40:
            tips.append('🏜️ Low humidity - Increase irrigation and consider mulching to retain soil moisture.')
        
        # Precipitation-based tips
        if precipitation > 10:
            tips.append('🌧️ Heavy rainfall expected - Check drainage systems and avoid fertilizer application to prevent nutrient loss.')
        elif precipitation > 5:
            tips.append('☔ Moderate rain expected - Good for arecanut growth, but monitor for waterlogging in low-lying areas.')
        elif precipitation == 0 and temp > 30:
            tips.append('☀️ Dry conditions - Increase irrigation frequency, especially for flowering and fruiting trees.')
        
        # Wind-based tips
        if wind_speed > 30:
            tips.append('💨 Strong winds expected - Secure young plants and check for potential damage to mature trees.')
        
        # Disease prevention tips based on weather
        if humidity > 70 and temp > 25:
            tips.append('🦠 Disease alert - High humidity and temperature create favorable conditions for fungal diseases. Apply preventive fungicides.')
        
        # Pest management tips
        if temp > 28 and humidity > 60:
            tips.append('🐛 Pest monitoring - Warm and humid conditions may increase pest activity. Check for red palm weevil and rhinoceros beetle.')
        
        # Irrigation tips
        if any(daily['precipitation_sum'][i] > 20 for i in range(3)):
            tips.append('🚰 Reduce irrigation - Heavy rain expected in coming days, adjust watering schedule accordingly.')
        
        # Harvesting tips
        current_month = datetime.now().month
        if current_month in [11, 12, 1, 2] and precipitation < 5:  # Harvesting season
            tips.append('🥥 Harvesting season - Dry weather is favorable for harvesting mature nuts. Check for optimal ripeness.')
        
        # General cultivation tips
        if temp >= 20 and temp <= 32 and humidity >= 60 and humidity <= 80:
            tips.append('✅ Optimal growing conditions - Perfect weather for arecanut cultivation. Continue regular care practices.')
        
        # Default tip if no specific conditions are met
        if not tips:
            tips.append('🌿 Weather conditions are stable - Continue regular monitoring and maintenance of your arecanut plantation.')
        
        return tips
    
    def get_weather_data(self, city, state, country):
        """Main method to get complete weather data"""
        try:
            # Get coordinates
            latitude, longitude, full_location = self.get_coordinates(city, state, country)
            
            # Fetch weather data
            weather_data = self.fetch_weather_data(latitude, longitude)
            
            # Process and return structured data
            return self.process_weather_data(weather_data, full_location)
            
        except requests.exceptions.Timeout:
            raise TimeoutError('Request timeout. Please try again.')
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'Network error: {str(e)}')
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f'An error occurred: {str(e)}')