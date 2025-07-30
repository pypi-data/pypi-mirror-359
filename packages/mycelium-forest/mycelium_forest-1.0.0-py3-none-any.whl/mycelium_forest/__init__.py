"""
MyceliumForest: Visualize Random Forest trees with mycelium-inspired network representations
"""

from .mycelium_forest import mycelium_forest, visualize_forest, RFTreeAnalyzer, demonstrate_single_tree_analysis

__version__ = "1.0.0"
__author__ = "Derya Kapisiz"

# making the main functions easily accessible
__all__ = ['mycelium_forest', 'visualize_forest', 'RFTreeAnalyzer', 'demonstrate_single_tree_analysis']