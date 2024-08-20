from langgraph.graph import StateGraph, START, END
from agents.planner import planner
from agents.graph_state import State
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver

from agents.generic_agent import chatbot
from agents.supervisor import supervisor
from agents.ai_expert import ai_expert
from agents.stock_trader import stock_trader


# create graph
graph_builder = StateGraph(State)

# add nodes
graph_builder.add_node("planner", planner)
graph_builder.add_node("generic", chatbot)

# add edges
graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "generic")

def next_agent(state):
    return state["agent"]


for agent in ["generic"]:
    graph_builder.add_edge(agent, END)

# compile graph


import sqlite3

conn = sqlite3.connect("db/graph.db", check_same_thread=False)
memory = SqliteSaver(conn)
# memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

graph.get_graph().draw_mermaid_png(output_file_path="graph.png")


# display graph
# from IPython.display import Image, display

# display(Image(graph.get_graph().draw_mermaid_png()))
