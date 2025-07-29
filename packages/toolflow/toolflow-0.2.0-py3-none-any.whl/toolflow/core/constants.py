RESPONSE_FORMAT_TOOL_NAME = "final_response_tool_internal"

DEFAULT_PARAMS = {
    "max_tool_calls": 5,
    "parallel_tool_execution": False,  # Default to sequential for playground-friendliness
    "response_format": None,
    "full_response": False,
    "graceful_error_handling": True
}
