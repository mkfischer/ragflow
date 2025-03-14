#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from abc import ABC
import pandas as pd
import requests
from agent.component.base import ComponentBase, ComponentParamBase


class OpenWeatherParam(ComponentParamBase):
    """
    Define the OpenWeather component parameters.
    """

    def __init__(self):
        super().__init__()
        self.api_key = "xxx"
        self.lang = "en"
        self.units = "metric"  # Options: metric, imperial
        self.error_code = {
            400: "Bad request - Invalid parameters",
            401: "Unauthorized - Invalid API key",
            404: "Not found - City not found",
            429: "Too Many Requests - API key rate limit exceeded",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }

    def check(self):
        self.check_empty(self.api_key, "OpenWeather API key")
        self.check_valid_value(self.lang, "Language",
                               ['en', 'zh_cn', 'fr', 'de', 'es', 'it', 'ru'])  # Add more as needed
        self.check_valid_value(self.units, "Units", ["metric", "imperial"])


class OpenWeather(ComponentBase, ABC):
    component_name = "OpenWeather"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = "".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return OpenWeather.be_output("No city name provided.")

        try:
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            final_url = base_url + "appid=" + self._param.api_key + "&q=" + ans + "&units=" + self._param.units + "&lang=" + self._param.lang
            weather_data = requests.get(final_url).json()

            if weather_data["cod"] == "404":
                return OpenWeather.be_output("**Error**: City not found.")
            elif weather_data["cod"] != 200:
                error_code = int(weather_data["cod"])
                error_message = self._param.error_code.get(error_code, "Unknown error")
                return OpenWeather.be_output(f"**Error**: {error_message}")
            else:
                # Extract relevant information
                temperature = weather_data["main"]["temp"]
                humidity = weather_data["main"]["humidity"]
                description = weather_data["weather"][0]["description"]
                city_name = weather_data["name"]
                country_code = weather_data["sys"]["country"]

                report = f"Weather in {city_name}, {country_code}:\n"
                report += f"Temperature: {temperature}°C\n"
                report += f"Humidity: {humidity}%\n"
                report += f"Description: {description}"

                return OpenWeather.be_output(report)

        except Exception as e:
            return OpenWeather.be_output("**Error**: " + str(e))
