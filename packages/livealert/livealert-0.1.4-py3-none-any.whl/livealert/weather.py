import os
import requests
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

def get_weather_alert(city):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            console.print("[red]Error: OpenWeather API key not found. Please set OPENWEATHER_API_KEY in your environment variables.[/red]")
            return

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error: Failed to get weather data. Status code: {response.status_code}[/red]")
            console.print(f"[red]Response: {response.text}[/red]")
            return
            
        data = response.json()
        
        table = Table(title=f"Weather Alert for {city}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Temperature", f"{data['main']['temp']}°C")
        table.add_row("Conditions", data['weather'][0]['description'])
        table.add_row("Humidity", f"{data['main']['humidity']}%")
        
        console.print(table)
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {str(e)}[/red]")
    except KeyError as e:
        console.print(f"[red]Data error: Missing key {str(e)} in response[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")