import os
from typing import Annotated, Sequence, TypedDict
from django.conf import settings
from django.db.models import Q
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Define Django-aware tools
@tool
def list_destinations(query: str = None, category_name: str = None) -> str:
    """
    Search and list destinations from the Vahad travel database.
    
    Args:
        query: Optional keywords to search in destination names, descriptions, or locations.
        category_name: Optional category name to filter (e.g. Beaches, Hills, Adventure).
        
    Returns:
        A list of matching destinations formatted as a string.
    """
    from vahad_app.models import Destination, Category
    
    qs = Destination.objects.all()
    if category_name:
        qs = qs.filter(category__name__icontains=category_name)
    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    results = []
    for d in qs[:8]:
        results.append(
            f"- **{d.name}** in {d.location}\n"
            f"  *Category*: {d.category.name}\n"
            f"  *Price Estimate*: ₹{d.price_estimate}\n"
            f"  *Best Time to Visit*: {d.best_time_to_visit}\n"
            f"  *Description*: {d.description}\n"
        )
        
    if not results:
        return "No destinations found matching the criteria."
    return "\n".join(results)

@tool
def get_destination_details(destination_name: str) -> str:
    """
    Retrieve full details for a specific destination by its name.
    
    Args:
        destination_name: The exact or close name of the destination to search for.
        
    Returns:
        Detailed information including name, location, category, price, best time, and description.
    """
    from vahad_app.models import Destination
    
    try:
        d = Destination.objects.filter(name__icontains=destination_name).first()
        if not d:
            return f"Destination '{destination_name}' not found."
            
        return (
            f"### {d.name}\n"
            f"- **Location**: {d.location}\n"
            f"- **Category**: {d.category.name}\n"
            f"- **Price Estimate**: ₹{d.price_estimate}\n"
            f"- **Best Time to Visit**: {d.best_time_to_visit}\n"
            f"- **Description**: {d.description}\n"
        )
    except Exception as e:
        return f"Error retrieving details: {str(e)}"

# Tools list
tools = [list_destinations, get_destination_details]
tool_node = ToolNode(tools)

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Define Call Model Node
def call_model(state: AgentState):
    messages = state["messages"]
    
    # Check for API keys
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        try:
            # Initialize Gemini model
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_key)
            llm_with_tools = llm.bind_tools(tools)
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"⚠️ Error calling Gemini API: {str(e)}")]}
            
    elif openai_key:
        from langchain_openai import ChatOpenAI
        try:
            # Initialize OpenAI model
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
            llm_with_tools = llm.bind_tools(tools)
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"⚠️ Error calling OpenAI API: {str(e)}")]}
            
    else:
        # Fallback to local database search if no API keys are provided
        from vahad_app.models import Destination
        
        last_message = messages[-1]
        user_query = last_message.content
        
        # Simple keywords parsing
        import re
        words = re.findall(r'\w+', user_query.lower())
        results = []
        for word in words:
            if len(word) > 3:  # avoid short filler words
                matches = Destination.objects.filter(
                    Q(name__icontains=word) | 
                    Q(description__icontains=word) | 
                    Q(location__icontains=word)
                )
                results.extend(matches)
                
        results = list(set(results)) # Deduplicate
        
        response_text = (
            "💡 **[Demo Mode]** No API keys were detected in the `.env` file.\n\n"
            "To activate the full AI agent with LangGraph's dynamic planning and reasoning, "
            "please add a `GEMINI_API_KEY` or `OPENAI_API_KEY` to the `.env` file at the root "
            "of the project and restart the server.\n\n"
        )
        
        if results:
            response_text += "I searched our travel database for your query and found these matching destinations:\n\n"
            for d in results[:5]:
                response_text += (
                    f"📍 **{d.name}** ({d.location})\n"
                    f"   *Category*: {d.category.name} | *Estimate*: ₹{d.price_estimate}\n"
                    f"   *Best Time*: {d.best_time_to_visit}\n"
                    f"   *{d.description}*\n\n"
                )
        else:
            response_text += "Here are some of our popular featured destinations:\n\n"
            featured = Destination.objects.filter(is_featured=True)[:3]
            for d in featured:
                response_text += (
                    f"📍 **{d.name}** ({d.location})\n"
                    f"   *Category*: {d.category.name} | *Estimate*: ₹{d.price_estimate}\n"
                    f"   *{d.description}*\n\n"
                )
                
        return {"messages": [AIMessage(content=response_text)]}

# Build workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# Compile graph with Memory Saver for session checkpointer
memory = MemorySaver()
compiled_agent = workflow.compile(checkpointer=memory)

# Function to run the agent
def ask_agent(session_id: str, message: str) -> str:
    config = {"configurable": {"thread_id": session_id}}
    
    # Run the compiled agent graph
    events = compiled_agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config
    )
    
    # Return the content of the final AIMessage in the output state
    last_msg = events["messages"][-1]
    return last_msg.content
