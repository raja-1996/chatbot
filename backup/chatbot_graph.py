from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition


# create graph
graph_builder = StateGraph(State)

# add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "chatbot")


from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string(":memory:")
graph = graph_builder.compile(checkpointer=memory)

# display graph
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))