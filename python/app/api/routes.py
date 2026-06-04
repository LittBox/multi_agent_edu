"""Legacy v1 routes — kept for backward compatibility."""

from fastapi import APIRouter, Request

from app.schemas.api_response import api_success

router = APIRouter(tags=["education-legacy"])


@router.get("/health")
async def health_check():
    return api_success(
        {"status": "ok", "service": "multi-agent-education", "agents": 5},
        message="Service is healthy",
    )


@router.get("/knowledge-graph")
async def get_knowledge_graph(request: Request):
    """Sample curriculum graph from in-memory KnowledgeGraph."""
    orch = request.app.state.orchestrator
    graph = orch.curriculum.knowledge_graph
    return api_success(
        {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "difficulty": n.difficulty,
                    "prerequisites": n.prerequisites,
                    "tags": n.tags,
                }
                for n in graph.nodes.values()
            ],
            "learning_order": graph.topological_sort(),
        },
        message="Sample knowledge graph fetched",
    )
