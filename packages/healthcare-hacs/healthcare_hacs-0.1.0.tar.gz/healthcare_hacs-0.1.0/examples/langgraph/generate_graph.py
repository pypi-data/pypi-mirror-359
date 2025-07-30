#!/usr/bin/env python3
"""
Generate visual representation of the HACS + LangGraph workflow.

This script creates a PNG image of the workflow graph using LangGraph's
built-in visualization capabilities.
"""

import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from graph import create_workflow_graph


def generate_workflow_image():
    """Generate and save the workflow graph image."""

    print("🎨 Generating LangGraph workflow visualization...")

    try:
        # Create the workflow graph
        app = create_workflow_graph()

        # Generate the graph visualization
        # This creates a PNG image of the workflow
        graph_image = app.get_graph().draw_mermaid_png()

        # Save the image
        output_path = "langgraph_workflow.png"
        with open(output_path, "wb") as f:
            f.write(graph_image)

        print(f"✅ Workflow graph saved as: {output_path}")
        print("📊 Graph shows the complete clinical assessment workflow")

        return output_path

    except ImportError as e:
        print(f"❌ Missing dependency for graph visualization: {e}")
        print("💡 Install with: pip install pygraphviz or pip install graphviz")
        return None

    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        return None


if __name__ == "__main__":
    generate_workflow_image()
