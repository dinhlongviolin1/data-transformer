import math
from typing import List

import pandas as pd
from fastapi import HTTPException

from ..models import TransformStep
from ..transformer import TransformerRegistry


def execute_pipeline(
    pipeline: List[TransformStep],
    df: pd.DataFrame,
    registry: TransformerRegistry,
    allowed=None,
) -> pd.DataFrame:
    for step in pipeline:
        name = step.name
        kwargs = step.args

        # Transformer lookup
        transformer = registry.get(name)
        if not transformer:
            raise HTTPException(400, detail=f"Unknown transformer: {name}")

        # Permission check
        if allowed is not None and name not in allowed:
            raise HTTPException(400, detail=f"Transformer not allowed: {name}")

        # Run transformer.validate()
        try:
            transformer.validate(df, kwargs)
        except Exception as e:
            raise HTTPException(422, detail=f"Validation failed for '{name}': {str(e)}")

        # Run Pipeline
        try:
            df = transformer.run(df, **kwargs)
        except Exception as e:
            raise HTTPException(422, detail=f"Simulation failed for '{name}': {str(e)}")
    return df


def safe_dict(records):
    def fix_nan(value):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return value

    return [{k: fix_nan(v) for k, v in row.items()} for row in records]
