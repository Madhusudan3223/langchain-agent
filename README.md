# Lang Graph Agent – Customer Support Workflow

##  Overview
This project implements a **Lang Graph Agent** that models a customer support workflow as **graph-based stages**.  
The agent, named **Langie**, processes customer queries across **11 stages**, persists state, integrates with MCP clients, and outputs a structured response payload.

---

##  Features
- **Graph-based Workflow (11 Stages)**
  1. INTAKE 📥 – accept_payload  
  2. UNDERSTAND 🧠 – parse_request_text, extract_entities  
  3. PREPARE 🛠️ – normalize_fields, enrich_records, add_flags_calculations  
  4. ASK ❓ – clarify_question  
  5. WAIT ⏳ – extract_answer, store_answer  
  6. RETRIEVE 📚 – knowledge_base_search, store_data  
  7. DECIDE ⚖️ – solution_evaluation, escalation_decision, update_payload  
  8. UPDATE 🔄 – update_ticket, close_ticket  
  9. CREATE ✍️ – response_generation  
  10. DO 🏃 – execute_api_calls, trigger_notifications  
  11. COMPLETE ✅ – output_payload  

- **State Persistence** using `TypedDict` to carry variables across stages.  
- **MCP Client Integration**:  
  - `COMMON` server → internal abilities (e.g., parsing, normalization, scoring).  
  - `ATLAS` server → external abilities (e.g., KB search, enrich records, notifications).  
- **Deterministic & Non-deterministic Stages**:  
  - Most stages run sequentially.  
  - **DECIDE** stage dynamically resolves or escalates based on solution score.  
- **Structured Final Payload** with ticket details, decision, solution score, customer response, and full logs.  

---
 Author

Madhusudan Mandal
madhumandal49@gmail.com
 +91 9304190347
