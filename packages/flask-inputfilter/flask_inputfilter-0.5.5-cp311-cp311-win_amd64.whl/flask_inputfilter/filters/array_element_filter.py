from __future__ import annotations

from typing import Any, Optional, Union

from flask_inputfilter.filters.base_filter import BaseFilter


class ArrayElementFilter(BaseFilter):
    """
    Filters each element in an array by applying one or more `BaseFilter`

    **Parameters:**

    - **element_filter** (*BaseFilter* | *list[BaseFilter]*): A filter or a
        list of filters to apply to each element in the array.

    **Expected Behavior:**

    Validates that the input is a list and applies the specified filter(s) to
    each element. If any element does not conform to the expected structure,
    a `ValueError` is raised.

    **Example Usage:**

    .. code-block:: python

        class TagInputFilter(InputFilter):
            def __init__(self):
                super().__init__()

                self.add('tags', validators=[
                    ArrayElementValidator(element_filter=IsStringValidator())
                ])
    """

    __slots__ = ("element_filter",)

    def __init__(
        self,
        element_filter: Union[BaseFilter, list[BaseFilter]],
        error_message: Optional[str] = None,
    ) -> None:
        self.element_filter = element_filter
        self.error_message = error_message

    def apply(self, value: Any) -> list[Any]:
        if not isinstance(value, list):
            return value

        result = []
        for element in value:
            if hasattr(self.element_filter, "apply"):
                result.append(self.element_filter.apply(element))
                continue

            elif isinstance(self.element_filter, list) and all(
                hasattr(v, "apply") for v in self.element_filter
            ):
                for filter_instance in self.element_filter:
                    element = filter_instance.apply(element)
                result.append(element)
                continue

            result.append(element)
        return result
