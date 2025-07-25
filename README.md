# 🌤️ Weather MCP Assistant – A Natural Language Interface for Meteorological Data

**Weather MCP Assistant** is a conversational AI system designed to understand natural language queries about historical weather observations. Powered by **OpenAI GPT-4o** and backed by a **MongoDB** dataset, this project demonstrates how to build an intelligent agent that interprets meteorological queries and responds with structured insights using a custom **FastMCP** framework.

---

## 📌 Features

- **Natural Language Interface**: Ask questions in plain English (e.g., "What was the temperature at KLAX on Jan 5th, 1984?")
- **FastMCP Integration**: Automatically maps user queries to structured tool functions.
- **MongoDB Weather Dataset**: Pulls data from a rich collection of historical weather observations.
- **OpenAI GPT-4o Integration**: Handles both tool selection and natural language formatting.
- **Robust Tooling**: Supports querying station metadata, temperature, wind, pressure, and summaries.
- **Command-Line Interaction**: Query in real-time through a terminal interface.

---

## 📁 Project Structure

- `main.py` — Core agent logic, FastMCP setup, and weather tools
- `db_connection.py` — MongoDB connection test and sample data preview
- `env.py` — Loads environment variables securely via `.env`
- `.env` — (Create this) API keys and MongoDB credentials
- `requirements.txt` — Python dependencies for the full system

---

## 🧠 System Description

This is an intelligent assistant composed of the following parts:

- **FastMCP**: Custom tool orchestration framework for language model-powered apps
- **OpenAI Wrapper**: Interfaces with GPT-4o for tool selection and output generation
- **MongoDB Connection**: Retrieves structured weather data from the database `sample_weatherdata`, collection `data`
- **Registered Tools**:
  - `get_station_metadata`
  - `get_temperature_at_time`
  - `get_wind_data`
  - `get_pressure_trend`
  - `get_all_stations_summary`

Each tool handles a specific data request and returns a clean response for formatting by the LLM.

---

