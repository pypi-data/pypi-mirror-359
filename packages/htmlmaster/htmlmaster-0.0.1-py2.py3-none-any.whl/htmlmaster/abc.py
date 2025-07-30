"""
Contains the abstract class: HTMLMaker.

NOTE: this module is private. All functions and objects are available in the main
`htmlmaster` namespace - use that instead.

"""

from abc import ABC, abstractmethod

__all__ = []


class HTMLMaker(ABC):
    """Make an html object."""

    def __init__(self, maincls: str = "main", style: str | None = None) -> None:
        self.__maincls = maincls
        self.__style = style

    def set_maincls(self, maincls: str, /) -> None:
        """Set the main class name."""
        self.__maincls = maincls

    def get_maincls(self) -> str | None:
        """Get the main class name."""
        return self.__maincls

    def setstyle(self, style: str | None, /) -> None:
        """Set the default css style."""
        self.__style = style

    def getstyle(self, default: str = "") -> str:
        """Get the default css style."""
        return default if self.__style is None else self.__style

    @abstractmethod
    def make(self) -> str:
        """Make a string representation of the html object."""

    def show(self) -> "HTMLRepr":
        """
        Show the html object.

        Returns
        -------
        HTMLRepr
            Represents an html object.

        """
        return HTMLRepr(self.make())

    def print(self) -> str:
        """
        Print the string representation of the html tree.

        Returns
        -------
        StrRepr
            Represents a string.

        """
        return StrRepr(self.make())


class HTMLRepr:
    """Represents an html object."""

    def __init__(self, html_str: str, /) -> None:
        self.__html_str = html_str

    def _repr_html_(self) -> str:
        return self.__html_str


class StrRepr:
    """Represents a string."""

    def __init__(self, html_str: str, /) -> None:
        self.__html_str = html_str

    def __repr__(self) -> str:
        return self.__html_str
