from langgraph.graph import END, START, StateGraph, MessagesState
from langchain.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .config import llm
from .prompts.prompts import system_prompt
from .tools.tools import ALL_TOOLS_LIST, SAFE_TOOLS, RISKY_TOOLS
from src.persistence import DynamoDBSaver

# binding llm woth tools
llm_with_tools = llm.bind_tools(ALL_TOOLS_LIST)


def assistant_node(state: MessagesState):
    messages = state["messages"]

    if not isinstance(messages[0], SystemMessage):
        messages = [system_prompt] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# routing
def route_tools(state: MessagesState):
    """check which tools which tools 'IA need to useand route to the good node"""

    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END

    tool_name = last_message.tool_calls[0]["name"]

    if tool_name == "initiate_refund":
        return "risky_tools"
    return "safe_tools"


# Graph
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant_node)
builder.add_node("safe_tools", ToolNode(SAFE_TOOLS))
builder.add_node("risky_tools", ToolNode(RISKY_TOOLS))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    route_tools,
    {"safe_tools": "safe_tools", "risky_tools": "risky_tools", END: END},
)
# Les deux chemins reviennent à l'assistant
builder.add_edge("safe_tools", "assistant")
builder.add_edge("risky_tools", "assistant")


# local developement
# memory = MemorySaver()


# 4. COMPILATION AVEC DYNAMODB
# On connecte le graphe à la table qu'on vient de créer
memory = DynamoDBSaver(table_name="AgentCheckpoints")


graph = builder.compile(checkpointer=memory, interrupt_before=["risky_tools"])
