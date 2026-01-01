"""This module defines a FastMCP server for Google Maps Platform operations."""
import httpx
import os
import re
import json
import asyncio
import googlemaps
import sys
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
from openai import OpenAI
from prompts import *
from dotenv import load_dotenv
load_dotenv()

#OPENAI_API_KEY="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"

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

GOOGLE_MCP_URL = os.getenv("GOOGLE_MCP_URL")

google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY")


#####################################################################################################################
##################################### Distance Summarizer #####################################################
#####################################################################################################################

def summarize_get_distance(output):
    """
    Summarizes the 'body' text of provided articles.
    """
        
    if not output:
        return "No content available to summarize."

    full_text_to_summarize = output

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": Get_Distance_Summarize},
                {"role": "user", "content": full_text_to_summarize}
                ]
            )
        summary = completion.choices[0].message.content
            
    except Exception as e:
        #print(f"Error summarizing article {i+1}: {e}")
        summary = f"Error generating unified summary: {e}"

    return summary

#####################################################################################################################
##################################### Directions Summarizer #####################################################
#####################################################################################################################

def summarize_get_directions(output):
    """
    Summarizes the 'body' text of provided articles.
    """
        
    if not output:
        return "No content available to summarize."

    full_text_to_summarize = output

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": Get_Directions_Summarize},
                {"role": "user", "content": full_text_to_summarize}
                ]
            )
        summary = completion.choices[0].message.content
            
    except Exception as e:
        #print(f"Error summarizing article {i+1}: {e}")
        summary = f"Error generating unified summary: {e}"

    return summary


######################################################################################################################
##################################### Weather Summarizer #########################################################
######################################################################################################################


def summarize_weat_data(data_dict):
    """
    Summarize dictionary response into key details like temperature, feels-like temperature,
        precipitation, wind direction, and wind speed
    Args:
        data_dict: A dictionary containing the parsed response from the API.

    """
    # Navigate the nested dictionary structure to extract the required values
    content = data_dict.get('result', {}).get('structuredContent', {}) #

    temperature = content.get('temperature', {}).get('degrees') #
    feels_like_temperature = content.get('feelsLikeTemperature', {}).get('degrees') #
    precipitation_percent = content.get('precipitation', {}).get('probability', {}).get('percent') #
    wind_direction = content.get('wind', {}).get('direction', {}).get('cardinal') #
    wind_speed = content.get('wind', {}).get('speed', {}).get('value') #

    # Create the final results dictionary
    extracted_data = {
        'Temperature': temperature,
        'feelsLikeTemperature': feels_like_temperature,
        'precipitation': precipitation_percent,
        'wind-direction': wind_direction,
        'wind-speed': wind_speed
    }

    try:
        # Convert the dictionary to a JSON formatted string before sending to the API
        extracted_data_as_string = json.dumps(extracted_data, indent=4) #
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": Get_Weather_Summarize},
                {"role": "user", "content": extracted_data_as_string}
                ]
            )
        extracted_data_summary = completion.choices[0].message.content
            
    except Exception as e:
        #print(f"Error summarizing article {i+1}: {e}")
        extracted_data_summary = f"Error generating weather summary: {e} + {extracted_data}"
    
    return extracted_data_summary



#################################################################################################################################
#################################################################################################################################

#---------------
# settings
#---------------
# these host, port, transport settings only apply if run using python
host=os.environ.get("FASTMCP_HOST", "0.0.0.0")
port=os.environ.get("FASTMCP_PORT", 8080)
transport=os.environ.get("FASTMCP_TRANSPORT", "stdio")  # stdio, streamable-http, sse

#google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY")
#gmaps = googlemaps.Client(key="AIzaSyAROmYKgbOWzB2NJv-OcBTww94Z1-oWUng")

gmaps = googlemaps.Client(key=google_maps_api_key)


#-------------
# helpers
#-------------
allowed_modes = ["driving", "walking", "bicycling", "transit"]
def assert_mode(mode: str):
    assert mode in allowed_modes, f"ERROR: '{mode}' is not one of the allowed modes: {allowed_modes}"

allowed_input_types = ["textquery", "phonenumber"]
def assert_input_type(input_type: str):
    assert input_type in allowed_input_types, f"ERROR: '{input_type}' is not one of the allowed inpute types: {allowed_input_types}"


#-----------------------
# initialize fastmcp
#-----------------------
# https://gofastmcp.com/servers/fastmcp#server-configuration
mcp = FastMCP(
    name="GoogleMapsServer",
    warn_on_duplicate_tools=True,
)


#-------------------
# direction tools
#-------------------
@mcp.tool()
async def get_directions(origin: str, destination: str, mode: str="driving") -> str:
    """Gives step-by-step instructions to get from origin to destination using a particular mode of transport
    Args:
        origin (str): originating address
        destination (str): destination address
        mode (str, optional): mode of transportation. Valid options are: driving, walking, bicycling, transit

    Returns:
         JSON dump in string format having 
         - summary : Indicating primary route
         - total_distance : Total distance between origin and destination
         - total_duration : Total driving duration between origin and destination 
         - Steps - Dictionary object having sequential instructions which customer should take in order to reach destination. 
         - Each step would comprise of : 
            - Instruction : Driving instruction
            - Distance - distance from last step
            - duration - Total driving duration between last step and current step
    """
    try:
        assert_mode(mode)
    except AssertionError as e:
        # print(e) # Replaced print with a return
        return json.dumps({"error": str(e)}, separators=(',', ':'))

    results = gmaps.directions(origin, destination, mode)

    if results:
        shortest_route = results[0]

        output = {
            "summary": shortest_route['summary'],
            "total_distance": shortest_route['legs'][0]['distance']['text'],
            "total_duration": shortest_route['legs'][0]['duration']['text'],
            "steps": []
        }
        
        for leg in shortest_route['legs']:
            for step in leg['steps']:
                output["steps"].append({
                    "instruction": step['html_instructions'],
                    "distance": step['distance']['text'],
                    "duration": step['duration']['text']
                })
        
        #return json.dumps(output, separators=(',', ':'))
        result = summarize_get_directions(json.dumps(output, separators=(',', ':')))
        return result
        #return shortest_route['summary']
    else:
        return "No directions found for the specified locations."

#--------------------------
# distance matrix tools
#--------------------------
@mcp.tool()
async def get_distance(origin: str, destination: str, mode: str="driving") -> str:
    """Finds the distance and travel time between two locations for a mode of transportation
    Args:
        origin (str): originating address
        destination (str): destination address
        mode (str): mode of travel (driving, walking, bicycling, transit)

    Returns:
        dictionary (JSON) of total distance, total travel time duration, and mode of travel
    """
    try:
        assert_mode(mode)
    except AssertionError as e:
        # print(e) # Replaced print with a return
        return json.dumps({"error": str(e)}, separators=(',', ':'))

    results = gmaps.distance_matrix(origin, destination, mode)

    if results:
        rows = results.get('rows', [])
        if not rows: # Check if rows is empty
            return "No distance information found for the specified locations." # More specific message

        shortest_distance_elements = rows[0].get('elements', [])
        if not shortest_distance_elements or 'distance' not in shortest_distance_elements[0] or 'duration' not in shortest_distance_elements[0]:
            return "No distance information found for the specified locations." # More specific message

        # At this point, we expect elements[0] to have distance and duration
        element = shortest_distance_elements[0]

        # Additional check for status if available, e.g. "ZERO_RESULTS"
        if element.get('status') == 'ZERO_RESULTS':
            return "No distance information found for the specified locations (ZERO_RESULTS)."

        output = {
            "total_distance": element['distance']['text'],
            "total_duration": element['duration']['text'],
            "mode": mode,
        }
        #return json.dumps(output, separators=(',', ':'))

        result = summarize_get_distance(json.dumps(output, separators=(',', ':')))
        return result
        
    else:
        return "No distance information found for the specified locations." # Generic message for no results


#-------------------
# geocoding tools
#-------------------
@mcp.tool()
async def get_geocode(address: str) -> Optional[Dict[str, Any]]:
    """
    Args:
        address (str): can be address or the name of a place

    Returns:
        dictionary (JSON) with the geocode (latitude & longitude) of the address
    """
    results = gmaps.geocode(address)

    if results:
        geocode = results[0]

        output = {
            "lat": geocode['geometry']['location']['lat'],
            "lng": geocode['geometry']['location']['lng'],
        }

        return json.dumps(output, separators=(',', ':'))
    else:
        return "Address not found"


#-------------------
# places tools
#-------------------
@mcp.tool()
async def find_place(input: str, input_type: str="textquery", fields: list=["place_id", "formatted_address", "name", "geometry", "types", "rating"]) -> Optional[Dict[str, Any]]:
    """Find/query a place with the provided name
    Args:
        input (str): name of the place you're looking for. provide more details if possible (i.e. city, country, etc.) for better accuracy. can also be the establishment type (i.e. bakery, bank, etc.)
        input_type (str, optional): the type of query, it can be a textquery or phonenumber query
        fields (list, optional): list of fields to query for

    Returns:
        dictionary (JSON) of with basic information of the top result based on input query. basic information inclulde:
        - name
        - place_id
        - address
        - location (latitude, longitude)
        - establishment type
        - average rating
    """
    try:
        assert_input_type(input_type)
    except AssertionError as e:
        # print(e) # Replaced print with a return
        return json.dumps({"error": str(e)}, separators=(',', ':'))

    results = gmaps.find_place(input, input_type, fields)

    if results:
        try:
            place = results.get('candidates', {})[0]
        except IndexError:
            return "No such place found"

        output = {
            "name": place['name'],
            "place_id": place['place_id'],
            "formatted_address": place['formatted_address'],
            "location": place['geometry']['location'],
            "types": place['types'],
            "rating": place.get('rating', None),
        }
        return json.dumps(output, separators=(',', ':'))


@mcp.tool()
async def place_nearby(location: dict, radius: int, place_type: str) -> Optional[Dict[str, Any]]:
    """Find types of places within a radius of a location (latitude, longitude)
    Args:
        location (dict): dictionary with 'lat' and 'lng' as keys and values are the latitude and longitude respectively
        radius (int): search area radius in meters (i.e. 2500 = 2.5km)
        place_type (str): type of place you're looking for (i.e. "italian restaurant", "hotel", etc.)

    Returns:
        dictionary (JSON) of establishment names (key) and their place_id (value)
    """
    results = gmaps.places_nearby(location, radius, place_type)
    output = {}

    if results:
        places_nearby = results.get('results', {})

        for place in range(len(places_nearby)):
            place_name = places_nearby[place]['name']
            place_id = places_nearby[place]['place_id']

            output[place_name] = place_id

        return json.dumps(output, separators=(',', ':'))
    else:
        return "Nothing nearby that matches the search criteria was found."


@mcp.tool()
async def place_details(place_id: str, fields: list=["name", "formatted_address", "formatted_phone_number", "website", "types", "rating", "user_ratings_total"]) -> Optional[Dict[str, Any]]:
    """
    Args:
        place_id (str): place_id of the place, which can be obtained via find_place() or place_nearby()
        fields (list, optional): list of fields to query for

    Returns:
        dictionary (JSON) of with details of provided place. details inclulde:
        - name
        - address
        - phone number
        - website
        - establishment type
        - average rating
        - total rating count
    """
    results = gmaps.place(place_id, fields)

    if results:
        details = results.get('result', {})
        if not details: # Check if details dict is empty
            return "No details found for the specified place."

        output = {
            "name": details.get('name'), # Use .get() for all potentially missing keys
            "formatted_address": details.get('formatted_address'),
            "formatted_phone_number": details.get('formatted_phone_number'),
            "website": details.get('website'),
            "types": details.get('types'), # If types is critical and always present, direct access might be okay
            "rating": details.get('rating'),
            "user_ratings_total": details.get('user_ratings_total', 0), # Existing .get with default for this one
        }
        # Filter out None values from output to keep it clean if some fields are missing
        output = {k: v for k, v in output.items() if v is not None}

        if not output.get("name"): # If essential info like name is missing after .get()
             return "Essential place details (e.g. name) are missing."

        return json.dumps(output, separators=(',', ':'))
    else:
        return "No such place found." # This handles case where 'results' itself is None

###################################################
####Weather tool##################################
###################################################


@mcp.tool()
async def get_google_weather(location: str) -> str:
    """
    Fetches real-time weather data for a given location from Google's Grounding Lite MCP.
    Args:
        location: The name of the city or coordinates.
    Returns:
        A summary containing details around temperature, feels-like temperature,
        precipitation, wind direction, and wind speed at given location
    """

    headers = {
        "X-Goog-Api-Key": google_maps_api_key,
        "Content-Type": "application/json"
    }
    
    # Payload follows the MCP tool call standard
    payload = {
        "jsonrpc": "2.0", # MUST be at the top level
        "id": 1,  # Required by Google's MCP server
        "method": "tools/call",
        "params": {
            "name": "lookup_weather",
            "arguments": {
                "location": {
                    "address" : location
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GOOGLE_MCP_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            weather_data = summarize_weat_data(data)
            #return f"Error : {type(data)} and json is {data}"
            return weather_data
            # Handle potential error messages in the JSON response body
        #    if "error" in data:
        #        return f"API Error: {data['error'].get('message', 'Unknown error')}"
                
        #    return data.get("result", "No weather data found.")
        except httpx.HTTPStatusError as e:
            #Capturing the specific error body from Google often reveals the exact missing parameter
            return f"HTTP {e.response.status_code} Error: {e.response.text}"
        except Exception as e:
            return f"Error connecting to Google Weather: {str(e)}"


#----------------
# main
#----------------
# https://gofastmcp.com/deployment/running-server
if __name__ == "__main__":
    #asyncio.run(mcp.run(transport=transport, host=host, port=port))
    try:
        if transport == "stdio":
            # For stdio transport, don't pass host and port
            mcp.run(transport=transport)
        else:
            # For HTTP-based transports, pass host and port
            mcp.run(transport=transport, host=host, port=port)
    except KeyboardInterrupt:
        print("> FastMCP Google Maps Server stopped by user.", file=sys.stderr)
    except Exception as e:
        print(f"> FastMCP Google Maps Server encountered error: {e}", file=sys.stderr)
    finally:
        print("> FastMCP Google Maps Server exiting.", file=sys.stderr)