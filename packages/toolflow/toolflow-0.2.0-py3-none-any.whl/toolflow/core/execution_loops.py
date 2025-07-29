# src/toolflow/core/execution_loops.py
from typing import Any, Generator, AsyncGenerator
import asyncio
from .adapters import Handler
from .utils import filter_toolflow_params
from .constants import RESPONSE_FORMAT_TOOL_NAME
from .tool_execution import execute_tools, execute_tools_async, MaxToolCallsError

# ===== GLOBAL ASYNC YIELD FREQUENCY CONFIGURATION =====

_ASYNC_YIELD_FREQUENCY = 0  # Default: disabled

def set_async_yield_frequency(frequency: int) -> None:
    """Set the global async yield frequency for streaming operations."""
    global _ASYNC_YIELD_FREQUENCY
    if frequency < 0:
        raise ValueError("async_yield_frequency must be >= 0")
    _ASYNC_YIELD_FREQUENCY = frequency

def get_async_yield_frequency() -> int:
    """Get the current global async yield frequency."""
    return _ASYNC_YIELD_FREQUENCY

def sync_execution_loop(
    handler: Handler,
    **kwargs: Any,
) -> Any:
    """Synchronous execution loop for tool calling."""

    (kwargs,
     max_tool_calls,
     parallel_tool_execution,
     response_format,
     full_response,
     graceful_error_handling) = filter_toolflow_params(**kwargs)
    
    tools = kwargs.get("tools", [])
    messages = kwargs.get("messages", [])
    
    response_format_tool = handler.get_response_format_tool(response_format)
    
    if not tools and not response_format_tool:
        response = handler.call_api(**kwargs)
        text, _, raw_response = handler.parse_response(response)
        # Check if max tokens was reached
        if hasattr(handler, 'check_max_tokens_reached'):
            handler.check_max_tokens_reached(response)
        return raw_response if full_response else text
    
    # If we have a response format tool, add it to tools
    if response_format_tool:
        tools.append(response_format_tool)
    tool_schemas, tool_map = handler.prepare_tool_schemas(tools)
    tool_map.pop(RESPONSE_FORMAT_TOOL_NAME, None)
    
    kwargs["tools"] = tool_schemas
    for _ in range(max_tool_calls):
        response = handler.call_api(**kwargs)
        text, tool_calls, raw_response = handler.parse_response(response)
        
        # Check if max tokens was reached
        if hasattr(handler, 'check_max_tokens_reached'):
            handler.check_max_tokens_reached(response)

        if not tool_calls:
            # If no tool calls but response_format is specified, try to parse text as JSON
            if response_format_tool and text is not None:
                try:
                    import json
                    parsed_json = json.loads(text)
                    parsed = response_format.model_validate(parsed_json)
                    if full_response:
                        # For full response, replace the content with parsed model
                        try:
                            # OpenAI format
                            raw_response.choices[0].message.content = parsed
                        except (AttributeError, TypeError):
                            # Anthropic format
                            if hasattr(raw_response, 'content') and raw_response.content:
                                for block in raw_response.content:
                                    if hasattr(block, 'text'):
                                        block.text = parsed
                                        break
                        return raw_response
                    else:
                        return parsed
                except json.JSONDecodeError as e:
                    # If JSON parsing fails when response_format is specified, raise an error
                    raise ValueError(f"Response parsing failed to get structured output: {e}") from e
                except Exception:
                    # Re-raise validation errors and other exceptions
                    raise
            return raw_response if full_response else text
        
        if response_format_tool:
            for tool_call in tool_calls:
                if tool_call["function"]["name"] == RESPONSE_FORMAT_TOOL_NAME:
                    # Extract the structured data from the tool call arguments
                    parsed = handler.parse_structured_output(tool_call, response_format)
                    return raw_response if full_response else parsed

        # Add assistant message with tool calls to conversation
        messages.append(handler.build_assistant_message(text, tool_calls, raw_response))
        
        tool_results = execute_tools(tool_calls, tool_map, parallel_tool_execution, graceful_error_handling)
        messages.extend(handler.build_tool_result_messages(tool_results))

    if response_format:
        raise MaxToolCallsError("Max tool calls reached without getting structured output. Try increasing the max_tool_calls parameter.", max_tool_calls)
    raise MaxToolCallsError("Max tool calls reached before completing the response. Try increasing the max_tool_calls parameter.", max_tool_calls)

async def async_execution_loop(
    handler: Handler,
    **kwargs: Any,
) -> Any:
    """Asynchronous execution loop for tool calling."""

    (kwargs,
     max_tool_calls,
     parallel_tool_execution,
     response_format,
     full_response,
     graceful_error_handling) = filter_toolflow_params(**kwargs)
    
    tools = kwargs.get("tools", [])
    if "messages" not in kwargs:
        kwargs["messages"] = []
    
    response_format_tool = handler.get_response_format_tool(response_format)
    
    if not tools and not response_format_tool:
        response = await handler.call_api_async(**kwargs)
        text, _, raw_response = handler.parse_response(response)
        # Check if max tokens was reached
        if hasattr(handler, 'check_max_tokens_reached'):
            handler.check_max_tokens_reached(response)
        return raw_response if full_response else text
    
    # If we have a response format tool, add it to tools
    if response_format_tool:
        tools.append(response_format_tool)
    tool_schemas, tool_map = handler.prepare_tool_schemas(tools)
    tool_map.pop(RESPONSE_FORMAT_TOOL_NAME, None)
    
    kwargs["tools"] = tool_schemas
    for _ in range(max_tool_calls):
        response = await handler.call_api_async(**kwargs)
        text, tool_calls, raw_response = handler.parse_response(response)
        
        # Check if max tokens was reached
        if hasattr(handler, 'check_max_tokens_reached'):
            handler.check_max_tokens_reached(response)

        if not tool_calls:
            # If no tool calls but response_format is specified, try to parse text as JSON
            if response_format_tool and text is not None:
                try:
                    import json
                    parsed_json = json.loads(text)
                    parsed = response_format.model_validate(parsed_json)
                    if full_response:
                        # For full response, replace the content with parsed model
                        try:
                            # OpenAI format
                            raw_response.choices[0].message.content = parsed
                        except (AttributeError, TypeError):
                            # Anthropic format
                            if hasattr(raw_response, 'content') and raw_response.content:
                                for block in raw_response.content:
                                    if hasattr(block, 'text'):
                                        block.text = parsed
                                        break
                        return raw_response
                    else:
                        return parsed
                except json.JSONDecodeError as e:
                    # If JSON parsing fails when response_format is specified, raise an error
                    raise ValueError(f"Response parsing failed to get structured output: {e}") from e
                except Exception:
                    # Re-raise validation errors and other exceptions
                    raise
            return raw_response if full_response else text
        
        if response_format_tool:
            for tool_call in tool_calls:
                if tool_call["function"]["name"] == RESPONSE_FORMAT_TOOL_NAME:
                    # Extract the structured data from the tool call arguments
                    parsed = handler.parse_structured_output(tool_call, response_format)
                    return raw_response if full_response else parsed
            
        # Add assistant message with tool calls to conversation  
        kwargs["messages"].append(handler.build_assistant_message(text, tool_calls, raw_response))
        
        tool_results = await execute_tools_async(tool_calls, tool_map, graceful_error_handling)
        kwargs["messages"].extend(handler.build_tool_result_messages(tool_results))

    if response_format:
        raise MaxToolCallsError("Max tool calls reached without getting structured output. Try increasing the max_tool_calls parameter.", max_tool_calls)
    raise MaxToolCallsError("Max tool calls reached before completing the response. Try increasing the max_tool_calls parameter.", max_tool_calls)

def sync_streaming_execution_loop(
    handler: Handler,
    **kwargs: Any,
) -> Generator[Any, None, None]:
    """Synchronous streaming execution loop with tool calling support."""
    (kwargs,
     max_tool_calls,
     parallel_tool_execution,
     response_format,
     full_response,
     graceful_error_handling) = filter_toolflow_params(**kwargs)
    
    tools = kwargs.get("tools", [])
    messages = kwargs.get("messages", [])
    
    # If no tools, just do simple streaming
    if not tools:
        response = handler.call_api(**kwargs)
        for text, _, raw_chunk in handler.accumulate_streaming_response(response):
            if full_response:
                yield raw_chunk
            elif text:
                yield text
        return
    
    # Prepare tools for tool calling
    response_format_tool = handler.get_response_format_tool(response_format)
    if response_format_tool:
        tools.append(response_format_tool)
    tool_schemas, tool_map = handler.prepare_tool_schemas(tools)
    tool_map.pop(RESPONSE_FORMAT_TOOL_NAME, None)
    
    kwargs["tools"] = tool_schemas
    remaining_tool_calls = max_tool_calls
    
    while remaining_tool_calls > 0:
        # Stream the response
        response = handler.call_api(**kwargs)
        
        accumulated_content = ""
        accumulated_tool_calls = []
        
        # Process the streaming response
        for text, partial_tool_calls, raw_chunk in handler.accumulate_streaming_response(response):
            # Accumulate content for tool calls
            if text:
                accumulated_content += text
            
            # Yield based on full_response setting
            if full_response:
                yield raw_chunk
            elif text:
                yield text
            
            # Accumulate tool calls (they come at the end of streaming)
            if partial_tool_calls:
                accumulated_tool_calls.extend(partial_tool_calls)
        
        # Check if we have tool calls to execute
        if accumulated_tool_calls:
            if response_format_tool:
                # Handle structured output
                for tool_call in accumulated_tool_calls:
                    if tool_call["function"]["name"] == RESPONSE_FORMAT_TOOL_NAME:
                        parsed = handler.parse_structured_output(tool_call, response_format)
                        # For structured output, we don't continue streaming
                        return parsed if not full_response else {"parsed": parsed}
            
            # Add assistant message with tool calls to conversation
            # Use None for content if no text was accumulated to preserve context for summarization
            content = accumulated_content if accumulated_content else None
            messages.append(handler.build_assistant_message(content, accumulated_tool_calls, None))
            
            # Execute tools
            tool_results = execute_tools(accumulated_tool_calls, tool_map, parallel_tool_execution, graceful_error_handling)
            messages.extend(handler.build_tool_result_messages(tool_results))
            
            # Update kwargs with new messages for next iteration
            kwargs["messages"] = messages
            remaining_tool_calls -= 1
            
            # Continue the loop for next streaming response (accumulators reset at loop start)
            continue
        else:
            # No tool calls, streaming is complete
            break
    
    if remaining_tool_calls <= 0:
        raise MaxToolCallsError("Max tool calls reached without a valid response", max_tool_calls)

def async_streaming_execution_loop(
    handler: Handler,
    **kwargs: Any,
) -> AsyncGenerator[Any, None]:
    """Asynchronous streaming execution loop with tool calling support."""
    (kwargs,
     max_tool_calls,
     parallel_tool_execution,
     response_format,
     full_response,
     graceful_error_handling) = filter_toolflow_params(**kwargs)

    async def internal_generator():
        
        tools = kwargs.get("tools", [])
        messages = kwargs.get("messages", [])
        
        # If no tools, just do simple streaming
        if not tools:
            chunk_count = 0
            response = await handler.call_api_async(**kwargs)
            async for text, _, raw_chunk in handler.accumulate_streaming_response_async(response):
                yield raw_chunk if full_response else text
                
                # Yield control to event loop for concurrency
                # By default disabled because we assume the underline provider handles this
                yield_freq = get_async_yield_frequency()
                if yield_freq > 0: 
                    chunk_count += 1
                    if chunk_count % yield_freq == 0:
                        await asyncio.sleep(0)
            return
        
        # Prepare tools for tool calling
        response_format_tool = handler.get_response_format_tool(response_format)
        if response_format_tool:
            tools.append(response_format_tool)
        tool_schemas, tool_map = handler.prepare_tool_schemas(tools)
        tool_map.pop(RESPONSE_FORMAT_TOOL_NAME, None)
        
        kwargs["tools"] = tool_schemas
        remaining_tool_calls = max_tool_calls
        
        while remaining_tool_calls > 0:
            # Stream the response
            response = await handler.call_api_async(**kwargs)
            
            accumulated_content = ""
            accumulated_tool_calls = []
            chunk_count = 0
            # Process the streaming response
            async for text, partial_tool_calls, raw_chunk in handler.accumulate_streaming_response_async(response):
                # Accumulate content for tool calls
                if text:
                    accumulated_content += text
                
                # Yield based on full_response setting
                if full_response:
                    yield raw_chunk
                elif text:
                    yield text
                
                # Accumulate tool calls (they come at the end of streaming)
                if partial_tool_calls:
                    accumulated_tool_calls.extend(partial_tool_calls)
                
                # Yield control to event loop for concurrency (by default disabled)
                # By default disabled because we assume the underline provider handles this
                yield_freq = get_async_yield_frequency()
                if yield_freq > 0:
                    chunk_count += 1
                    if chunk_count % yield_freq == 0:
                        await asyncio.sleep(0)
            
            # Check if we have tool calls to execute
            if accumulated_tool_calls:
                if response_format_tool:
                    # Handle structured output
                    for tool_call in accumulated_tool_calls:
                        if tool_call["function"]["name"] == RESPONSE_FORMAT_TOOL_NAME:
                            parsed = handler.parse_structured_output(tool_call, response_format)
                            # For structured output, we don't continue streaming
                            yield parsed if not full_response else {"parsed": parsed}
                            return
                
                # Add assistant message with tool calls to conversation
                # Use None for content if no text was accumulated to preserve context for summarization
                content = accumulated_content if accumulated_content else None
                messages.append(handler.build_assistant_message(content, accumulated_tool_calls, None))
                
                # Execute tools (this properly yields via asyncio.gather/run_in_executor)
                tool_results = await execute_tools_async(accumulated_tool_calls, tool_map, graceful_error_handling)
                messages.extend(handler.build_tool_result_messages(tool_results))
                
                # Update kwargs with new messages for next iteration
                kwargs["messages"] = messages
                remaining_tool_calls -= 1
                
                # Continue the loop for next streaming response (accumulators reset at loop start)
                continue
            else:
                # No tool calls, streaming is complete
                break
        
        if remaining_tool_calls <= 0:
            raise MaxToolCallsError("Max tool calls reached without a valid response", max_tool_calls)
    
    return internal_generator()
