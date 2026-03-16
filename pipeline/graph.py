from langgraph.graph import StateGraph, END
from pipeline.state import PipelineState
from pipeline.agents.reddit_scraper import scrape_and_deduplicate
from pipeline.agents.narrative_evaluator import evaluate_narrative_resolution
from pipeline.agents.consensus_evaluator import evaluate_resolution_consensus
from pipeline.agents.pii_anonymizer import anonymize_pii
from pipeline.agents.pii_verifier import verify_pii_removal
from pipeline.agents.editorial_polisher import polish_editorial
from pipeline.agents.final_qa import run_final_qa
from pipeline.agents.supabase_storage import store_to_supabase


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("reddit_scraper", scrape_and_deduplicate)
    graph.add_node("narrative_evaluator", evaluate_narrative_resolution)
    graph.add_node("consensus_evaluator", evaluate_resolution_consensus)
    graph.add_node("pii_anonymizer", anonymize_pii)
    graph.add_node("pii_verifier", verify_pii_removal)
    graph.add_node("editorial_polisher", polish_editorial)
    graph.add_node("final_qa", run_final_qa)
    graph.add_node("supabase_storage", store_to_supabase)

    graph.set_entry_point("reddit_scraper")

    # Early exit if filter stages produce nothing
    graph.add_conditional_edges(
        "reddit_scraper",
        lambda s: "narrative_evaluator" if s.raw_stories else END,
    )
    graph.add_conditional_edges(
        "narrative_evaluator",
        lambda s: "consensus_evaluator" if s.filtered_stories else END,
    )
    graph.add_conditional_edges(
        "consensus_evaluator",
        lambda s: "pii_anonymizer" if s.consensus_filtered_stories else END,
    )

    graph.add_edge("pii_anonymizer", "pii_verifier")
    graph.add_edge("pii_verifier", "editorial_polisher")
    graph.add_edge("editorial_polisher", "final_qa")
    graph.add_edge("final_qa", "supabase_storage")
    graph.add_edge("supabase_storage", END)

    return graph.compile()
