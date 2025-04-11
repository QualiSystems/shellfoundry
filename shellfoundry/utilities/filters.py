from __future__ import annotations

from typing import ClassVar

from attrs import define, field

GEN_ONE = "gen1"
GEN_TWO = "gen2"
LAYER_ONE = "layer1"
NO_FILTER = "all"
GEN_ONE_FILTER = "gen1"
GEN_TWO_FILTER = "gen2"
LAYER_ONE_FILTER = "layer-1"
SEPARATOR = "/"


class BaseFilter:
    FILTER_TYPE: ClassVar[str]

    def passes(self, template_name: str) -> bool:
        return self.FILTER_TYPE == NO_FILTER or self.FILTER_TYPE in template_name


class GenOneFilter(BaseFilter):
    FILTER_TYPE: ClassVar[str] = GEN_ONE_FILTER


class GenTwoFilter(BaseFilter):
    FILTER_TYPE: ClassVar[str] = GEN_TWO_FILTER


class LayerOneFilter(BaseFilter):
    FILTER_TYPE: ClassVar[str] = LAYER_ONE_FILTER


class NoFilter(BaseFilter):
    FILTER_TYPE: ClassVar[str] = NO_FILTER


@define
class CompositeFilter:
    template_type: str | None = NO_FILTER
    filters: dict[str, type[BaseFilter]] = field(
        init=False,
        default={
            GEN_ONE: GenOneFilter,
            GEN_TWO: GenTwoFilter,
            LAYER_ONE: LayerOneFilter,
            NO_FILTER: NoFilter,
        },
    )

    def __attrs_post_init__(self):
        if not self.template_type:
            self.template_type = NO_FILTER

    def passes(self, template_name):
        return self.filters.get(self.template_type, NoFilter)().passes(template_name)
