from __future__ import annotations

from typing import Optional, Union, Literal
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, validator




Number = Union[PositiveFloat, PositiveInt]  


class NumericLimit(BaseModel):
    """
    A quantitative control expressed as either a maximum or minimum value.
    Examples:
      • NumericLimit(type="max", value=60, unit="%")       → ≤ 60 % site coverage
      • NumericLimit(type="min", value=2,  unit="spaces")  → ≥ 2 parking spaces
    """
    type: Literal["max", "min"] = Field(
        ...,
        description='Choose "max" for an upper limit (≤) or "min" for a lower limit (≥).',
    )
    value: Number = Field(
        ...,
        description="Magnitude of the control (must be positive).",
    )
    unit: str = Field(
        ...,
        description='Unit of measurement, e.g. "%", "m", "levels", "spaces".',
    )

    @validator("unit")
    def unit_must_be_recognised(cls, v):
        allowed = {"%", "m", "levels", "spaces"}
        if v not in allowed:
            raise ValueError(f"unit must be one of {allowed}")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# PlanSA “Planning & Design Code – Quantitative Assessment” schema
# ─────────────────────────────────────────────────────────────────────────────
TbcOrNa = Literal["TBC", "N/A"]


class PlanningQuantitativeAssessment(BaseModel):
    # ─── Basic site figures ───────────────────────────────────────────────
    site_coverage: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 60 % site coverage.",
    )
    building_height_levels: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 2 levels.",
    )
    building_height_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 9 m building height.",
    )
    wall_height_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 7 m wall height.",
    )

    # ─── Street setbacks ────────────────────────────────────────────────
    primary_street_setback_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 5.5 m primary-street setback.",
    )
    secondary_street_setback: Optional[Union[NumericLimit, TbcOrNa]] = Field(
        None,
        description=(
            "Secondary‐street setback (corner sites). Example: “N/A” when lot has "
            "only one street frontage."
        ),
    )

    # ─── Side setbacks ─────────────────────────────────────────────────
    lower_side_boundary_wall_height_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 3 m boundary-wall height on lower side.",
    )
    lower_side_boundary_wall_length_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: max 11.5 m boundary-wall length on lower side.",
    )
    lower_side_clear_setback_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 0.9 m clear setback to opposite boundary.",
    )

    upper_side_base_setback_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 0.9 m base upper-side setback.",
    )
    upper_side_extra_formula: Optional[str] = Field(
        None,
        description="Example: ‘additional setback = ⅓ of wall height above 3 m’.",
    )

    # ─── Rear setbacks ─────────────────────────────────────────────────
    lower_rear_setback_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 4 m lower-rear setback.",
    )
    upper_rear_setback_m: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 6 m upper-rear setback.",
    )

    # ─── Qualitative / deferred items ──────────────────────────────────
    boundary_walls: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Rules for boundary walls (fire-rating, maximum combined length, etc.). "
            "Marked ‘TBC’ until PlanSA issues numeric caps."
        ),
    )
    cut_and_fill: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Earth-works limits (depth of cut / height of fill). ‘TBC’ means limits "
            "not yet quantified for this zone."
        ),
    )
    overlooking: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Privacy measures for upper-storey windows and balconies. Usually set "
            "by glazing type or screening; numeric offset may be ‘TBC’."
        ),
    )
    tree_planting: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Minimum on-site tree planting (species & spacing). ‘TBC’ until council "
            "publishes exact numbers."
        ),
    )
    streetscape: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description="Design measures to enhance streetscape character; numeric ratios often ‘TBC’.",
    )
    garage_setback: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Distance of garage façade behind main building line. Numeric value "
            "commonly 0.5–1 m; currently ‘TBC’."
        ),
    )
    garage_opening: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Maximum width of garage door relative to frontage (e.g. ≤ 50 %). "
            "Marked ‘TBC’ if not specified."
        ),
    )
    driveway_crossover: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Standards for driveway crossovers (width & location). ‘TBC’ where council "
            "policy pending."
        ),
    )
    private_open_space: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Required private open-space area per dwelling (e.g. min 24 m²). ‘TBC’ "
            "if not yet determined."
        ),
    )
    soft_landscaping: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Percentage of site that must remain pervious/landscaped. Often 15–20 %; "
            "‘TBC’ while awaiting confirmation."
        ),
    )
    street_trees: Optional[Union[str, TbcOrNa]] = Field(
        None,
        description=(
            "Council-planted street trees required per frontage length. Numeric spacing "
            "or species list may be ‘TBC’."
        ),
    )

    # ─── Parking ────────────────────────────────────────────────────────
    car_parking_spaces: Optional[NumericLimit] = Field(
        None,
        description="Example guideline: min 2 on-site parking spaces.",
    )
