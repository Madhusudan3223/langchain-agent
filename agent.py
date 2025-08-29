# Import necessary libraries
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
import re
import random
import json

# --- 1. Define the Agent's State ---
class CustomerSupportState(TypedDict):
    """
    Represents the state of our customer support workflow.
    """
    customer_name: str
    email: str
    query: str
    priority: str
    ticket_id: int
    logs: List[str]
    parsed_text: str
    entities: Dict[str, str]
    normalized_fields: Dict[str, str]
    enriched_records: Dict[str, any]
    calculated_flags: Dict[str, str]
    clarifying_question: Optional[str]
    user_answer: Optional[str]
    retrieved_data: str
    solution_score: int
    decision: str
    final_response: str

# --- 2. Mock MCP Clients ---
def mcp_client_common(ability_name: str, state: CustomerSupportState) -> any:
    """Simulates routing an ability to the COMMON server."""
    print(f"  [MCP Client -> COMMON] Executing ability: {ability_name}")
    if ability_name == "parse_request_text":
        return state['query']
    elif ability_name == "normalize_fields":
        return {"normalized_ticket_id": f"TCKT-{state['ticket_id']:07d}"}
    elif ability_name == "add_flags_calculations":
        if state.get('priority', '').lower() == 'high':
            return {'sla_risk': 'High'}
        return {'sla_risk': 'Normal'}
    elif ability_name == "solution_evaluation":
        return random.randint(90, 100) # Varied for successful demo
    elif ability_name == "response_generation":
        customer_name = state.get("customer_name", "Customer")
        retrieved_info = state.get("retrieved_data", "No specific information was found.")
        return f"Hello {customer_name},\n\nRegarding your ticket #{state['ticket_id']}, our system suggests: {retrieved_info}. This issue has now been marked as resolved.\n\nThank you for contacting us."
    elif ability_name == "update_payload":
        return "Payload updated with decision + score."
    return None

def mcp_client_atlas(ability_name: str, state: CustomerSupportState) -> any:
    """Simulates routing an ability to the ATLAS server."""
    print(f"  [MCP Client -> ATLAS] Executing ability: {ability_name}")
    if ability_name == "extract_entities":
        query = state['query']
        entities = {}
        product_match = re.search(r"product (\w+)", query, re.IGNORECASE)
        if product_match:
            entities['product'] = product_match.group(1)
        return entities
    elif ability_name == "enrich_records":
        email = state.get('email', '')
        if "jane" in email:
            return {"sla": "Gold", "historical_ticket_count": 5}
        return {"sla": "Standard", "historical_ticket_count": 1}
    elif ability_name == "clarify_question":
        if not state.get('entities', {}).get('product'):
            return "It seems a product was not mentioned. Could you please specify which product this query is about?"
        return None
    elif ability_name == "extract_answer":
        return state.get('user_answer', '')
    elif ability_name == "knowledge_base_search":
        product = state.get('entities', {}).get('product')
        if product:
            return f"KB Article 201: Troubleshooting steps for Product {product}."
        return "KB Article 101: General FAQ and support contact information."
    elif ability_name == "escalation_decision":
        return f"Ticket {state['ticket_id']} assigned to Human Agent Tier 2."
    elif ability_name == "update_ticket":
        return f"Success: Ticket {state['ticket_id']} status updated to 'Resolved'."
    elif ability_name == "close_ticket":
        return f"Success: Ticket {state['ticket_id']} has been closed."
    elif ability_name == "execute_api_calls":
        return f"API Call Success: CRM record for ticket {state['ticket_id']} updated."
    elif ability_name == "trigger_notifications":
        email = state.get('email', 'N/A')
        return f"Notification Success: Final response sent to {email}."
    elif ability_name == "store_answer":
        return f"Stored answer for ticket {state['ticket_id']}."
    elif ability_name == "store_data":
        return f"Stored knowledge base info for ticket {state['ticket_id']}."
    return None

# --- 3. Stage Functions ---
def stage_intake(state: CustomerSupportState) -> CustomerSupportState:
    log_message = f"Stage 1: INTAKE - Accepted payload for ticket_id: {state.get('ticket_id', 'N/A')}."
    state['logs'] = state.get('logs', [])
    state['logs'].append(log_message)
    print(log_message)
    return state

def stage_understand(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 2: UNDERSTAND - Parsing request and extracting entities."
    state['logs'].append(log_message)
    print(log_message)
    state['parsed_text'] = mcp_client_common("parse_request_text", state)
    state['entities'] = mcp_client_atlas("extract_entities", state)
    state['logs'].append(f"  - Extracted entities: {state['entities']}")
    print(f"  - Extracted entities: {state['entities']}")
    return state

def stage_prepare(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 3: PREPARE - Normalizing fields, enriching records, and calculating flags."
    state['logs'].append(log_message)
    print(log_message)
    state['normalized_fields'] = mcp_client_common("normalize_fields", state)
    state['enriched_records'] = mcp_client_atlas("enrich_records", state)
    state['calculated_flags'] = mcp_client_common("add_flags_calculations", state)
    state['logs'].extend([
        f"  - Normalized Fields: {state['normalized_fields']}",
        f"  - Enriched Records: {state['enriched_records']}",
        f"  - Calculated Flags: {state['calculated_flags']}"
    ])
    print(f"  - Normalized Fields: {state['normalized_fields']}\n  - Enriched Records: {state['enriched_records']}\n  - Calculated Flags: {state['calculated_flags']}")
    return state

def stage_ask(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 4: ASK - Checking if clarification is needed."
    state['logs'].append(log_message)
    print(log_message)
    state['clarifying_question'] = mcp_client_atlas("clarify_question", state)
    log = f"  - Question for user: {state['clarifying_question']}" if state['clarifying_question'] else "  - No clarification needed."
    state['logs'].append(log)
    print(log)
    return state

def stage_wait(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 5: WAIT - Capturing and storing user's answer."
    state['logs'].append(log_message)
    print(log_message)
    state['user_answer'] = "The user replied: It's about Product C."
    extracted = mcp_client_atlas("extract_answer", state)
    store_result = mcp_client_atlas("store_answer", state)
    state['logs'].append(f"  - Extracted Answer: {extracted}")
    state['logs'].append(f"  - Store Answer Result: {store_result}")
    print(f"  - Stored Answer: {extracted}")
    return state

def stage_retrieve(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 6: RETRIEVE - Searching knowledge base."
    state['logs'].append(log_message)
    print(log_message)
    state["retrieved_data"] = mcp_client_atlas("knowledge_base_search", state)
    store_result = mcp_client_atlas("store_data", state)
    state['logs'].append(f"  - Retrieved data: {state['retrieved_data']}")
    state['logs'].append(f"  - Store Data Result: {store_result}")
    print(f"  - Retrieved data: {state['retrieved_data']}")
    return state

def stage_decide(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 7: DECIDE - Evaluating solution and making escalation decision."
    state['logs'].append(log_message)
    print(log_message)
    score = mcp_client_common("solution_evaluation", state)
    state["solution_score"] = score
    state['logs'].append(f"  - Solution Score: {score}")
    print(f"  - Solution Score: {score}")
    if score < 90:
        state["decision"] = "ESCALATE"
        log = "  - Decision: Score is < 90. Escalating."
        state['logs'].append(log)
        print(log)
        escalation_result = mcp_client_atlas("escalation_decision", state)
        state['logs'].append(f"  - Escalation Result: {escalation_result}")
        print(f"  - Escalation Result: {escalation_result}")
    else:
        state["decision"] = "RESOLVE"
        log = "  - Decision: Score is >= 90. Resolving."
        state['logs'].append(log)
        print(log)
    update_result = mcp_client_common("update_payload", state)
    state['logs'].append(f"  - Update Payload Result: {update_result}")
    print(f"  - Update Payload Result: {update_result}")
    return state

def stage_update(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 8: UPDATE - Updating and closing ticket."
    state['logs'].append(log_message)
    print(log_message)
    update_result = mcp_client_atlas("update_ticket", state)
    close_result = mcp_client_atlas("close_ticket", state)
    state['logs'].append(f"  - Update Result: {update_result}")
    state['logs'].append(f"  - Close Result: {close_result}")
    print(f"  - Update Result: {update_result}\n  - Close Result: {close_result}")
    return state

def stage_create(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 9: CREATE - Generating final customer response."
    state['logs'].append(log_message)
    print(log_message)
    state["final_response"] = mcp_client_common("response_generation", state)
    state['logs'].append(f"  - Generated Response: '{state['final_response']}'")
    print(f"  - Generated Response: '{state['final_response']}'")
    return state

def stage_do(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 10: DO - Executing final API calls and notifications."
    state['logs'].append(log_message)
    print(log_message)
    api_result = mcp_client_atlas("execute_api_calls", state)
    notification_result = mcp_client_atlas("trigger_notifications", state)
    state['logs'].append(f"  - API Call Result: {api_result}")
    state['logs'].append(f"  - Notification Result: {notification_result}")
    print(f"  - API Call Result: {api_result}\n  - Notification Result: {notification_result}")
    return state

def stage_complete(state: CustomerSupportState) -> CustomerSupportState:
    log_message = "Stage 11: COMPLETE - Workflow finished. Outputting final payload."
    state['logs'].append(log_message)
    print(log_message)
    final_payload = {
        "ticket_id": state.get("ticket_id"),
        "customer_name": state.get("customer_name"),
        "decision": state.get("decision"),
        "solution_score": state.get("solution_score"),
        "final_response_to_customer": state.get("final_response"),
        "full_log": state.get("logs")
    }
    print("\n--- FINAL STRUCTURED PAYLOAD ---")
    print(json.dumps(final_payload, indent=2))
    print("------------------------------")
    return state

# --- 4. Conditional Routing ---
def should_wait(state: CustomerSupportState) -> str:
    print("  [Router] Checking if a question was asked...")
    if state.get("clarifying_question"):
        return "wait"
    else:
        return "continue"

def should_escalate(state: CustomerSupportState) -> str:
    print("  [Router] Checking escalation decision...")
    if state.get("decision") == "ESCALATE":
        return "escalate"
    else:
        return "resolve"

# --- 5. Build Graph ---
workflow = StateGraph(CustomerSupportState)
workflow.add_node("INTAKE", stage_intake)
workflow.add_node("UNDERSTAND", stage_understand)
workflow.add_node("PREPARE", stage_prepare)
workflow.add_node("ASK", stage_ask)
workflow.add_node("WAIT", stage_wait)
workflow.add_node("RETRIEVE", stage_retrieve)
workflow.add_node("DECIDE", stage_decide)
workflow.add_node("UPDATE", stage_update)
workflow.add_node("CREATE", stage_create)
workflow.add_node("DO", stage_do)
workflow.add_node("COMPLETE", stage_complete)

workflow.set_entry_point("INTAKE")
workflow.add_edge("INTAKE", "UNDERSTAND")
workflow.add_edge("UNDERSTAND", "PREPARE")
workflow.add_edge("PREPARE", "ASK")
workflow.add_conditional_edges("ASK", should_wait, {"wait": "WAIT", "continue": "RETRIEVE"})
workflow.add_edge("WAIT", "RETRIEVE")
workflow.add_edge("RETRIEVE", "DECIDE")
workflow.add_conditional_edges("DECIDE", should_escalate, {"escalate": END, "resolve": "UPDATE"})
workflow.add_edge("UPDATE", "CREATE")
workflow.add_edge("CREATE", "DO")
workflow.add_edge("DO", "COMPLETE")
workflow.add_edge("COMPLETE", END)

app = workflow.compile()
print("\n✅ Agent graph compiled with all 11 stages.\n")

# --- DEMO RUN ---
if __name__ == "__main__":
    sample_input = {
        "customer_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "query": "My subscription for Product B is not working.",
        "priority": "High",
        "ticket_id": 54321
    }
    print("🚀 STARTING DEMO RUN...")
    final_state = app.invoke(sample_input)
    print("🏁 DEMO RUN COMPLETE.")
