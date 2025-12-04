from pydantic import BaseModel, Field

class BBox(BaseModel):
    """
    Bounding box with unnormalized pixel coordinates

    Coordinates are in pixel values, not normalized (0-1000) scale.
    """

    x1: int = Field(description="Left x coordinate (pixels)", ge=0)
    y1: int = Field(description="Top y coordinate (pixels)", ge=0)
    x2: int = Field(description="Right x coordinate (pixels)", ge=0)
    y2: int = Field(description="Bottom y coordinate (pixels)", ge=0)

    class Config:
        extra = "forbid"

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Convert to tuple format (x1, y1, x2, y2) for PIL crop()"""
        return (self.x1, self.y1, self.x2, self.y2)

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary format"""
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}

    @classmethod
    def from_dict(cls, d: dict[str, int]) -> "BBox":
        """Create from dictionary"""
        return cls(x1=d["x1"], y1=d["y1"], x2=d["x2"], y2=d["y2"])

    @classmethod
    def from_normalized(
        cls, x1: int, y1: int, x2: int, y2: int, width: int, height: int
    ) -> "BBox":
        """
        Create from normalized coordinates (0-1000 scale)

        Args:
            x1, y1, x2, y2: Normalized coordinates (0-1000)
            width, height: Image dimensions in pixels

        Returns:
            BBox with pixel coordinates
        """
        bx1 = int(x1 / 1000 * width)
        by1 = int(y1 / 1000 * height)
        bx2 = int(x2 / 1000 * width)
        by2 = int(y2 / 1000 * height)

        # Ensure correct ordering
        if bx1 > bx2:
            bx1, bx2 = bx2, bx1
        if by1 > by2:
            by1, by2 = by2, by1

        return cls(x1=bx1, y1=by1, x2=bx2, y2=by2)

    def width(self) -> int:
        """Calculate width of bounding box"""
        return abs(self.x2 - self.x1)

    def height(self) -> int:
        """Calculate height of bounding box"""
        return abs(self.y2 - self.y1)

    def area(self) -> int:
        """Calculate area of bounding box"""
        return self.width() * self.height()

    def validate_ordering(self) -> "BBox":
        """Ensure x1 < x2 and y1 < y2, swap if needed"""
        x1, x2 = (self.x1, self.x2) if self.x1 <= self.x2 else (self.x2, self.x1)
        y1, y2 = (self.y1, self.y2) if self.y1 <= self.y2 else (self.y2, self.y1)
        return BBox(x1=x1, y1=y1, x2=x2, y2=y2)