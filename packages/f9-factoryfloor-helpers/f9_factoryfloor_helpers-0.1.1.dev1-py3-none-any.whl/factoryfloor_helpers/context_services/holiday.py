"""
Holiday-related classes for context services.
"""

from pydantic import BaseModel
from datetime import datetime
from nagerapi import NagerObjectAPI
from typing import List


class Holiday(BaseModel):
    """
    Represents a holiday with a name and date.

    Attributes:
        name: The name of the holiday
        date: The date of the holiday
    """
    name: str
    date: datetime


class HolidayBuilder:
    """
    Builder class for retrieving and formatting holiday information.

    This class uses the NagerObjectAPI to fetch holiday data for a specific country.

    Attributes:
        country: The country object from NagerObjectAPI
    """

    def __init__(self, country_code: str):
        """
        Initialize the HolidayBuilder with a country code.

        Args:
            country_code: The ISO country code (e.g., "US", "UK")
        """
        self.nager = NagerObjectAPI()
        self.country = self.nager.country(country_code)

    def get_next_public_holidays(self) -> List[Holiday]:
        """
        Get a list of upcoming public holidays for the specified country.

        Returns:
            A list of Holiday objects
        """
        holidays = []
        for holiday in self.country.next_public_holidays():
            holidays.append(Holiday(name=holiday.name, date=holiday.date))
        return holidays

    def get_date(self, holiday: Holiday) -> str:
        """
        Format a holiday date in YYYYMMDD format.

        Args:
            holiday: The Holiday object

        Returns:
            The formatted date string
        """
        return holiday.date.strftime("%Y%m%d")