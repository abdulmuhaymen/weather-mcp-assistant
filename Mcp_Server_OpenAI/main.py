from fastmcp import FastMCP
from openai_wrapper import OpenAIWrapper
from mongo import collection

import os
import datetime
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Step 1: Initialize FastMCP with name only
mcp = FastMCP("LeaveMCP")

# Step 2: Initialize and set the LLM
llm = OpenAIWrapper(api_key=OPENAI_API_KEY, model="gpt-4o")
mcp.set_llm(llm)

# Step 3: Set system prompt
mcp.set_system_prompt("""
You are a meteorological assistant that helps users interact with historical weather observation data stored in a MongoDB collection called data under the database sample_weatherdata. Your job is to assist users in querying and interpreting weather data—such as air temperature, pressure, wind, visibility, and sky condition—by extracting the station identifier (callLetters, e.g., "PLAT") and timestamps from natural language inputs. Always convert dates and times like "March 5th, 1984 at 3 PM" into ISO format (YYYY-MM-DDTHH:MM:SS).

When users ask for data, identify the station and time, then call the appropriate tool (e.g., get_station_metadata, get_temperature_at_time, get_pressure_trend, get_wind_data). If the user does not provide a station or time, ask for it or default to the latest available record. Be concise, clear, and technical, and always present your output in a readable, structured format..
""")

@mcp.tool()
def get_station_metadata(callLetters: str) -> dict:
    """Get metadata about a weather station given its call letters."""
    station = collection.find_one({"callLetters": callLetters})
    if station:
        return {
            "position": station.get("position"),
            "elevation": station.get("elevation"),
            "type": station.get("type"),
            "dataSource": station.get("dataSource"),
            "qualityControlProcess": station.get("qualityControlProcess"),
        }
    return {"error": "Station not found"}


@mcp.tool()
def get_temperature_at_time(callLetters: str, timestamp: str) -> dict:
    """Get air temperature for a station at a given ISO timestamp."""
    try:
        ts_obj = datetime.datetime.fromisoformat(timestamp)
        obs = collection.find_one({"callLetters": callLetters, "ts": ts_obj})
        if obs and "airTemperature" in obs:
            return obs["airTemperature"]
        return {"error": "No temperature data for this time"}
    except ValueError:
        return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}


@mcp.tool()
def get_wind_data(callLetters: str) -> dict:
    """Return latest wind info for the station."""
    doc = collection.find_one(
        {"callLetters": callLetters},
        sort=[("ts", -1)]  # sort by latest timestamp
    )
    if doc:
        return {
            "timestamp": doc["ts"].isoformat() if doc.get("ts") else None,  # Convert datetime to string
            "wind": doc.get("wind", "No wind data")
        }
    return {"error": "No data for this station"}


@mcp.tool()
def get_all_stations_summary() -> dict:
    """Return the count of documents per station."""
    pipeline = [
        {"$group": {"_id": "$callLetters", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return {"stations": list(collection.aggregate(pipeline))}


@mcp.tool()
def get_pressure_trend(callLetters: str, limit: int = 10) -> list:
    """Return the last N pressure values for a station."""
    cursor = collection.find({"callLetters": callLetters}).sort("ts", -1).limit(limit)
    trend = []
    for doc in cursor:
        pressure = doc.get("pressure")
        if pressure:
            trend.append({
                "ts": doc["ts"].isoformat() if doc.get("ts") else None,  # Convert datetime to string
                "pressure": pressure
            })
    return trend[::-1]  # oldest to newest


if __name__ == "__main__":
    print("TOOLS LOADED:", list(mcp.tools.keys()))
    mcp.run_stdio()