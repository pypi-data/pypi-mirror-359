import logging
from typing import Any

import pydantic

from sifts.analysis.types import FunctionTool, TreeExecutionContext, VulnerabilityAssessment

LOGGER = logging.getLogger(__name__)


async def format_response(
    _ctx: TreeExecutionContext | None,
    args: dict[str, Any],
) -> VulnerabilityAssessment | None:
    try:
        parsed = VulnerabilityAssessment.model_validate(
            args,
        )
    except pydantic.ValidationError:
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    except (TypeError, KeyError, AttributeError):
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    except Exception:
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    return parsed


FORMAT_RESPONSE = FunctionTool[VulnerabilityAssessment | None](
    name="format_response",
    description=(
        "Retrieves code and details using its ID from the global search. "
        "Use this after finding a relevant function with list_symbols. "
        "This will add the function to the available methods for analysis."
    ),
    params_json_schema={
        **VulnerabilityAssessment.model_json_schema(),
        "additionalProperties": False,
    },
    on_invoke_tool=format_response,
)
