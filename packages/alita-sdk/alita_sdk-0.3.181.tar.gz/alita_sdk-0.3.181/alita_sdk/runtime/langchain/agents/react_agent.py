import logging
from typing import Any, Optional, Callable
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

def create_react_agent_with_auto_continue(
    prompt: Any,
    model: Any,
    tools: list[BaseTool],
    memory: Optional[Any] = None,
    debug: bool = False
) -> Any:
    """
    Create a LangGraph React agent with auto-continue capability for when responses get truncated.
    This provides better handling of length-limited responses compared to traditional AgentExecutor.
    Uses simple in-memory checkpointing for auto-continue functionality.
    
    Args:
        prompt: The prompt template to use for the agent
        model: The language model to use
        tools: List of tools available to the agent
        memory: Optional memory store for checkpointing (will create MemorySaver if None)
        debug: Whether to enable debug mode
        
    Returns:
        A configured React agent with auto-continue capability
        
    Note: Requires LangGraph 0.5.x or higher that supports post_model_hook.
    """
    # Use simple in-memory checkpointer for auto-continue functionality if not provided
    if memory is None:
        memory = MemorySaver()
    
    # Set up parameters for the agent
    kwargs = {
        "prompt": prompt,
        "model": model,
        "tools": tools,
        "checkpointer": memory,
        "post_model_hook": _create_auto_continue_hook()  # Auto-continue hook
    }

    # Create the base React agent with langgraph's prebuilt function
    base_agent = create_react_agent(**kwargs)
    
    return base_agent

def _create_auto_continue_hook() -> Callable:
    """
    Create a post-model hook for LangGraph 0.5.x that detects truncated responses
    and adds continuation prompts.
    This checks if the last AI message was truncated and automatically continues if needed.
    """
    MAX_CONTINUATIONS = 3  # Maximum number of auto-continuations allowed
    
    def post_model_hook(state):
        messages = state.get("messages", [])
        
        # Count how many auto-continue messages we've already sent
        continuation_count = sum(
            1 for msg in messages 
            if isinstance(msg, HumanMessage) and 
            "continue your previous response" in msg.content.lower()
        )
        
        # Don't continue if we've reached the limit
        if continuation_count >= MAX_CONTINUATIONS:
            return state
            
        # Check if the last message is from AI and was truncated
        if messages and isinstance(messages[-1], AIMessage):
            last_ai_message = messages[-1]
            
            # Check for truncation indicators
            is_truncated = (
                hasattr(last_ai_message, 'response_metadata') and 
                last_ai_message.response_metadata.get('finish_reason') == 'length'
            ) or (
                # Fallback: check if message seems to end abruptly
                last_ai_message.content and 
                not last_ai_message.content.rstrip().endswith(('.', '!', '?', ':', ';'))
            )
            
            # Add continuation request if truncated
            if is_truncated:
                logger.info("Detected truncated response, adding continuation request")
                new_messages = messages.copy()
                new_messages.append(HumanMessage(content="Continue your previous response from where you left off"))
                return {"messages": new_messages}
        
        return state
        
    return post_model_hook

def get_langgraph_agent_with_auto_continue(
    prompt: Any,
    model: Any,
    tools: list[BaseTool],
    memory: Optional[Any] = None,
    debug: bool = False
) -> Any:
    """
    Create a LangGraph agent with auto-continue capability for when responses get truncated.
    This provides better handling of length-limited responses compared to traditional AgentExecutor.
    Uses simple in-memory checkpointing for auto-continue functionality.
    
    Args:
        prompt: The prompt template to use for the agent
        model: The language model to use
        tools: List of tools available to the agent
        memory: Optional memory store for checkpointing (will create MemorySaver if None)
        debug: Whether to enable debug mode
        
    Returns:
        A configured LangGraphAgentRunnable with auto-continue capability
        
    Note: Requires LangGraph 0.5.x or higher that supports post_model_hook.
    """
    from ...langchain.langraph_agent import LangGraphAgentRunnable
    
    # Use simple in-memory checkpointer for auto-continue functionality if not provided
    if memory is None:
        memory = MemorySaver()
    
    # Create the base React agent with auto-continue capability
    base_agent = create_react_agent_with_auto_continue(
        prompt=prompt,
        model=model,
        tools=tools,
        memory=memory,
        debug=debug
    )
    
    # Wrap the base agent in our custom LangGraphAgentRunnable to handle input properly
    # This ensures that our invoke() input handling logic is applied
    agent = LangGraphAgentRunnable(
        builder=base_agent.builder,
        config_type=base_agent.builder.config_schema,
        nodes=base_agent.nodes,
        channels=base_agent.channels,
        input_channels=base_agent.input_channels,
        stream_mode=base_agent.stream_mode,
        output_channels=base_agent.output_channels,
        stream_channels=base_agent.stream_channels,
        checkpointer=memory,
        interrupt_before_nodes=base_agent.interrupt_before_nodes,
        interrupt_after_nodes=base_agent.interrupt_after_nodes,
        debug=debug,
        store=base_agent.store, 
        schema_to_mapper=base_agent.schema_to_mapper
    )
    
    return agent
