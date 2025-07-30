"""hey MCP server tools.

Note: Ensure 'requests' and 'mcp' packages are installed and importable in your environment.
"""
import os
import json
import random
import requests
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("hey MCP")

def fetch_flight_data(url: str, params: dict) -> dict:
    """Fetch flight data from the hey API."""
    api_key = os.getenv('HEY_MCP_API_KEY')
    if not api_key:
        raise ValueError("HEY_MCP_API_KEY not set in environment.")
    params = {'access_key': api_key, **params}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def flights_with_airline(airline_name: str, number_of_flights: int) -> str:
    """MCP tool to get flights with a specific airline."""
    try:
        data = fetch_flight_data(
            'http://api.aviationstack.com/v1/flights',
            {'airline_name': airline_name}
        )
        filtered_flights = []
        data_list = data.get('data', [])
        number_of_flights = min(number_of_flights, len(data_list))

        # Sample random flights from the data list
        sampled_flights = random.sample(data_list, number_of_flights)

        for flight in sampled_flights:
            filtered_flights.append({
                'flight_number': flight.get('flight').get('iata'),
                'airline': flight.get('airline').get('name'),
                'departure_airport': flight.get('departure').get('airport'),
                'departure_timezone': flight.get('departure').get('timezone'),
                'departure_time': flight.get('departure').get('scheduled'),
                'arrival_airport': flight.get('arrival').get('airport'),
                'arrival_timezone': flight.get('arrival').get('timezone'),
                'flight_status': flight.get('flight_status'),
                'departure_delay': flight.get('departure').get('delay'),
                'departure_terminal': flight.get('departure').get('terminal'),
                'departure_gate': flight.get('departure').get('gate'),
            })
        return json.dumps(filtered_flights) if filtered_flights else (
            f"No flights found for airline '{airline_name}'."
        )
    except requests.RequestException as e:
        return f"Request error: {str(e)}"
    except (KeyError, ValueError, TypeError) as e:
        return f"Error fetching flights: {str(e)}"