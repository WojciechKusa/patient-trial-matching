"""Module containing utility functions"""
from enum import Enum


class Gender(Enum):
    """Enum type class for representing Gender in topics and clinical trials."""

    unknown = "U"
    male = "M"
    female = "F"
    all = "A"
