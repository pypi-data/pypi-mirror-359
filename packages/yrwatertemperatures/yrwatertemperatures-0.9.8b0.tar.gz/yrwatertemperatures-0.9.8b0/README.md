# Norway Water Temperature API Client
A Python package to fetch water temperature data from various locations in Norway.

[![GitHub release](https://img.shields.io/github/release/jornpe/yr-norwegian-water-temperatures?include_prereleases=&sort=semver&color=blue)](https://github.com/jornpe/Yr-norwegian-water-temperatures-integration/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![issues - Yr-norwegian-water-temperatures-integration](https://img.shields.io/github/issues/jornpe/yr-norwegian-water-temperatures)](https://github.com/jornpe/Yr-norwegian-water-temperatures-integration/issues)
[![Tests](https://github.com/jornpe/yr-norwegian-water-temperatures/actions/workflows/test.yml/badge.svg)](https://github.com/jornpe/yr-norwegian-water-temperatures/actions/workflows/test.yml)

## Installation
```
pip install yrwatertemperatures
```

## API key
To use this package, you need an API key from yr.no, see https://hjelp.yr.no/hc/no/articles/5949243432850-API-for-badetemperaturer for more info. 

## Usage
First, you'll need to get an API key from the provider of the water temperature data.

Then, you can use the package like this:

```python
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
```

## Data Structure
The `get_temperatures` method returns a list of `LocationData` objects. Each object has the following attributes:

`name` (str): The name of the location.

`location_id` (str): A unique identifier for the location.

`latitude` (float): The latitude of the location.

`longitude` (float): The longitude of the location.

`elevation` (int): The elevation of the location in meters.

`county` (str): The county where the location is.

`municipality` (str): The municipality where the location is.

`temperature` (float): The water temperature in Celsius.

`time` (datetime): The timestamp of the reading.

`source` (str): The source of the data (not always present).

## Development

For development and contributing to this package:

```bash
# Clone the repository
git clone https://github.com/jornpe/yr-norwegian-water-temperatures.git
cd yr-norwegian-water-temperatures

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=yrwatertemperatures --cov-report=html

# Format code
black .
isort .

# Type checking
mypy yrwatertemperatures
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [Releases](https://github.com/jornpe/yr-norwegian-water-temperatures/releases) for a detailed changelog.