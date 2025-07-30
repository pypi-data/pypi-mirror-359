from typing import Any
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError

class _IsValidAlias:
    """
    Validator that checks if a value is a valid alias string.
    """

    _INVALID_CHARS = set(' \t\n\r\x0b\x0c!@#$%^&*()[]{};:,/<>?\\|`~"\'')

    def __call__(self, value: Any) -> None:
        """
        Ensures that the provided value is a valid alias of type str and does not contain invalid characters.

        Parameters
        ----------
        value : Any
            The value to check.

        Raises
        ------
        OrionisContainerTypeError
            If the value is not of type str or contains invalid characters.
        """
        if not isinstance(value, str):
            raise OrionisContainerTypeError(
                f"Expected a string type for alias, but got {type(value).__name__} instead."
            )

        if any(char in self._INVALID_CHARS for char in value):
            raise OrionisContainerTypeError(
                f"Alias '{value}' contains invalid characters. "
                "Aliases must not contain whitespace or special symbols."
            )

# Exported singleton instance
IsValidAlias = _IsValidAlias()