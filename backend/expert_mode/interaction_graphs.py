from fastapi import APIRouter, Query
import networkx as nx
import json
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/expert/interaction/graph", tags=["expert_interaction_graph"])

# Import interaction data from main engine
from .interaction_engine import INTERACTION_DATABASE

@router.get("/network")
async def get_interaction_network(
    center: Optional[str] = Query(None, description="Center ingredient"),
    depth: int = Query(2, description="Network depth"),
    min_strength: float = Query(0.3, description="Minimum interaction strength")
):
    """Get network graph data for ingredient interactions"""
    try:
        G = nx.Graph()
        
        # Add all nodes
        for ing_id, ing_data in INTERACTION_DATABASE.items():
            G.add_node(ing_id, 
                      name=ing_data["name"],
                      size=30,
                      color=get_node_color(ing_id))
        
        # Add edges for interactions
        for ing_a, ing_data in INTERACTION_DATABASE.items():
            for ing_b, interaction in ing_data.get("interactions", {}).items():
                if ing_b in INTERACTION_DATABASE and interaction.get("strength", 0) >= min_strength:
                    G.add_edge(ing_a, ing_b,
                              weight=interaction.get("strength", 0.5),
                              type=interaction.get("type", "unknown"),
                              color=get_edge_color(interaction.get("type", "unknown")))
        
        # If center specified, get ego network
        if center and center in G:
            nodes = set([center])
            # Add neighbors up to depth
            current = set([center])
            for _ in range(depth):
                next_nodes = set()
                for node in current:
                    next_nodes.update(G.neighbors(node))
                nodes.update(next_nodes)
                current = next_nodes
            
            G = G.subgraph(nodes)
        
        # Convert to Cytoscape.js format
        cy_data = {
            "nodes": [],
            "edges": []
        }
        
        for node in G.nodes(data=True):
            cy_data["nodes"].append({
                "data": {
                    "id": node[0],
                    "label": node[1].get("name", node[0]),
                    "size": node[1].get("size", 30),
                    "color": node[1].get("color", "#94a3b8")
                }
            })
        
        for edge in G.edges(data=True):
            cy_data["edges"].append({
                "data": {
                    "source": edge[0],
                    "target": edge[1],
                    "weight": edge[2].get("weight", 0.5),
                    "type": edge[2].get("type", "unknown"),
                    "color": edge[2].get("color", "#94a3b8")
                }
            })
        
        return {
            "success": True,
            "data": cy_data,
            "stats": {
                "nodes": len(cy_data["nodes"]),
                "edges": len(cy_data["edges"]),
                "density": nx.density(G)
            }
        }
    except Exception as e:
        logger.error(f"Network graph error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/clusters")
async def get_interaction_clusters():
    """Get identified interaction clusters"""
    try:
        G = nx.Graph()
        
        # Build graph
        for ing_a, ing_data in INTERACTION_DATABASE.items():
            for ing_b in ing_data.get("interactions", {}).keys():
                if ing_b in INTERACTION_DATABASE:
                    G.add_edge(ing_a, ing_b)
        
        # Find communities using greedy modularity
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(G)
        
        clusters = []
        for i, comm in enumerate(communities):
            if len(comm) > 1:  # Only show clusters with multiple ingredients
                cluster_data = {
                    "id": i,
                    "name": f"Cluster {i+1}",
                    "ingredients": [],
                    "size": len(comm),
                    "risk_score": 0
                }
                
                for ing in comm:
                    ing_data = INTERACTION_DATABASE.get(ing, {})
                    cluster_data["ingredients"].append({
                        "id": ing,
                        "name": ing_data.get("name", ing),
                        "risk_level": ing_data.get("risk_level", "unknown")
                    })
                
                clusters.append(cluster_data)
        
        return {
            "success": True,
            "data": clusters
        }
    except Exception as e:
        logger.error(f"Clusters error: {e}")
        return {"success": False, "error": str(e)}

def get_node_color(ingredient_id: str) -> str:
    """Get color for node based on ingredient category/risk"""
    colors = {
        "retinol": "#f87171",
        "niacinamide": "#4ade80",
        "vitamin_c": "#fbbf24",
        "benzoyl_peroxide": "#f97316",
        "aha_bha": "#c084fc"
    }
    return colors.get(ingredient_id, "#94a3b8")

def get_edge_color(interaction_type: str) -> str:
    """Get color for edge based on interaction type"""
    colors = {
        "synergistic": "#4ade80",
        "antagonistic": "#f87171",
        "risk_amplifying": "#dc2626",
        "neutral": "#94a3b8"
    }
    return colors.get(interaction_type, "#94a3b8")