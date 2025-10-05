from __future__ import annotations
from copy import deepcopy
from litemapy import Region, Schematic

from const import Block, Coord, RegionNestingError


class RegionWrapper(Region):

    def __init__(self, width, height, length):

        if min(width, height, length) < 0:
            raise ValueError("RegionWrapper can not have negative width/height/length.")

        super().__init__(0, 0, 0, width, height, length)
        self.__sub_regions: list[RegionWrapper] = []

    def __str__(self) -> str:
        return f"RegionWrapper with dimmensions ({self.width}, {self.height}, {self.length})."

    def nest_region(self, sub_region: RegionWrapper, pos: Coord) -> None:
        x, y, z = pos
        if (
            x + sub_region.width > self.width
            or y + sub_region.height > self.height
            or z + sub_region.length > self.length
        ):
            raise RegionNestingError("Sub region does not fit in parent region.")

        sub_region_copy = deepcopy(sub_region)
        sub_region_copy._Region__x = x
        sub_region_copy._Region__y = y
        sub_region_copy._Region__z = z

        self.__sub_regions.append(sub_region_copy)

    def as_schematic(self, *args, **kwargs) -> Schematic:
        """
        Creates a schematic that contains that region at the origin.
        """
        self._flatten()
        return super().as_schematic(*args, **kwargs)

    def _flatten(self) -> None:

        if not self.__sub_regions:
            return

        for sub_region in self.__sub_regions:
            sub_region._flatten()

            for coord in sub_region.block_positions():
                block = sub_region[coord]
                if block == Block.AIR:
                    continue

                parent_coord = self._sub_to_parent_coord(sub_region, coord)

                if self[parent_coord] != Block.AIR:
                    raise RegionNestingError("Sub region blocks overlap with parent region blocks.")
                self[parent_coord] = block

        self.__sub_regions = []

    @staticmethod
    def _sub_to_parent_coord(sub_region: RegionWrapper, coord: Coord):
        local_x, local_y, local_z = coord
        return (
            local_x + sub_region.x,
            local_y + sub_region.y,
            local_z + sub_region.z,
        )
