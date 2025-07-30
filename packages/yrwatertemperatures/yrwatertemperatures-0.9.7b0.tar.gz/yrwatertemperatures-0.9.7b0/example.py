"""Example script to fetch and display water temperatures using the yrwatertemperatures package."""
import asyncio
from aiohttp import ClientSession, ClientError
from yrwatertemperatures import WaterTemperatures

API_KEY = "your_api_key_here"  # Replace with your actual API key

async def main() -> None:
    """Main function to fetch and display water temperatures."""
    async with ClientSession() as session:
        try:
            client = WaterTemperatures(API_KEY, session)
            temperatures = await client.async_get_all_water_temperatures()

            # Print the location and temperature
            for temp in temperatures:
                print(f"Location: {temp.name}, Temperature: {temp.temperature}°C")

        except (ClientError, Exception) as e:
            print(f"An error occurred: {e}")

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()

