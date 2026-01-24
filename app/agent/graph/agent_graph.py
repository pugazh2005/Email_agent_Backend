from langgraph.graph import StateGraph,START,END

from app.agent.nodes.send_reply import send_reply
from app.agent.nodes.human_review_node import human_review
from app.agent.nodes.classify_email import classify_email
from app.agent.nodes.persist_classification import persist_classification
from app.agent.nodes.read_email import read_email
from app.agent.nodes.retrieve_docs import retrieve_docs
from app.agent.nodes.route_to_bug_or_write import route_bug_or_write
from app.agent.nodes.bug_tracking import bug_tracking
from app.agent.state import EmailAgentState
from app.agent.nodes.write_response import write_response


def build_email_graph(checkpointer):
    builder=StateGraph(EmailAgentState)

    builder.add_node("read_email",read_email)
    builder.add_node("classify_email",classify_email)
    builder.add_node("persist_classification",persist_classification)
    builder.add_node("retrieve_docs",retrieve_docs)
    builder.add_node("bug_tracking",bug_tracking)
    builder.add_node("human_review",human_review)
    builder.add_node("send_reply",send_reply)
    builder.add_node("write_response",write_response)

    builder.add_edge(START,"read_email")
    builder.add_edge("read_email","classify_email")
    builder.add_edge("classify_email","persist_classification")
    builder.add_edge("persist_classification","retrieve_docs")
    builder.add_conditional_edges("retrieve_docs",
                                route_bug_or_write,
                                {"track_bug":"bug_tracking",
                                "response":"write_response"})
    builder.add_edge("bug_tracking","write_response")
    builder.add_edge("send_reply",END)
    
    return builder.compile(checkpointer=checkpointer)
    

