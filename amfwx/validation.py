"""Small form validation layer."""

from __future__ import annotations

import re


class ValidationError(ValueError):
    pass


def required(value):
    if value is None or str(value).strip() == "":
        raise ValidationError("Pflichtfeld")
    return value


def min_length(length):
    def check(value):
        if len(str(value)) < int(length):
            raise ValidationError(f"mindestens {length} Zeichen")
        return value
    return check


def max_length(length):
    def check(value):
        if len(str(value)) > int(length):
            raise ValidationError(f"hoechstens {length} Zeichen")
        return value
    return check


def pattern(regex, message="ungueltiges Format"):
    compiled = re.compile(regex)

    def check(value):
        if not compiled.fullmatch(str(value)):
            raise ValidationError(message)
        return value
    return check


def email(value):
    return pattern(r"[^@\s]+@[^@\s]+\.[^@\s]+", "ungueltige E-Mail")(value)


def integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError("ganze Zahl erwartet")


def number_range(minimum=None, maximum=None):
    def check(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Zahl erwartet")
        if minimum is not None and number < minimum:
            raise ValidationError(f"mindestens {minimum}")
        if maximum is not None and number > maximum:
            raise ValidationError(f"hoechstens {maximum}")
        return number
    return check


class Field:
    def __init__(self, name, widget, validators=None):
        self.name = name
        self.widget = widget
        self.validators = list(validators or [])
        self.error = ""

    def value(self):
        getter = getattr(self.widget, "text", None)
        return getter() if callable(getter) else str(getter or "")

    def validate(self):
        value = self.value()
        try:
            for validator in self.validators:
                value = validator(value)
            self.error = ""
            return True
        except ValidationError as error:
            self.error = str(error)
            return False


class Form:
    def __init__(self):
        self.fields = []

    def add(self, name, widget, validators=None):
        field = Field(name, widget, validators)
        self.fields.append(field)
        return field

    def validate(self):
        return all(field.validate() for field in self.fields)

    def errors(self):
        return {field.name: field.error for field in self.fields
                if field.error}

    def values(self):
        return {field.name: field.value() for field in self.fields}
