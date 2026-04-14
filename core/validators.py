import re


def validate_phone(value):
    if not re.match(r'^05\d{8}$', value):
        raise ValueError("Invalid phone number")


def validate_id_number(value):
    if not value.isdigit() or len(value) not in [8, 9]:
        raise ValueError("Invalid ID number")


def validate_name(value):
    if len(value) < 2:
        raise ValueError("Name too short")