from app.api.orchestrator import AgentOrchestrator 

#AgentOrchestrator 实例，让 API / Service 层每次都拿同一个编排器，而不是每次请求重新 new 一个
agent_orchestrator = AgentOrchestrator()