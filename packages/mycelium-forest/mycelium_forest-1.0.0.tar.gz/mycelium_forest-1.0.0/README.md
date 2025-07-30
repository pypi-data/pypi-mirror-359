# MyceliumForest 🍄

Visualize Random Forest trees with pretty mycelium-inspired network representations 🌞

## installation

pip install mycelium_forest

### explanation

inspired by the work of Hänsch & Hellwich on "Performance Assessment and Interpretation of Random Forests by Three-dimensional Visualizations"

base trunk placement represents the correlations between trees: the closer two trunks are, the more correlated are their predictions.
trees' alphas are defined by their oob strength. alpha is lost at each level for aesthetic reasons.
branch angles are Information Gain dependant (the wider the angle, the more IG there is). branch angles are tightened at each level for aesthetic reasons.
