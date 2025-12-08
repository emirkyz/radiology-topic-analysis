# Radiology Topic Analysis Dashboard

Github Pages Link : https://emirkyz.github.io/radiology-topic-analysis/

An interactive web dashboard showcasing NMF-based topic modeling results from radiology imaging journals.

## Features

- **Overview**: Model statistics, coherence scores chart, t-SNE visualization
- **Topic Explorer**: Interactive grid of all 25 topics with wordclouds and top words
- **Topic Relations**: Embedded interactive ECharts graph showing topic relationships
- **Temporal Trends**: Line charts and area charts showing topic evolution over time
- **Top Documents**: Browse representative documents for each topic


## Data Files

- `data/coherence_scores.json` - Topic coherence metrics and top words
- `data/diversity_scores.json` - Topic diversity metrics
- `data/top_docs.json` - Representative documents per topic
- `images/wordclouds/` - Wordcloud images for each topic
- `images/*.png` - Visualization images (t-SNE, temporal charts, etc.)
- `topic-graph.html` - Interactive topic relations graph

## Technologies Used

- Vanilla HTML/CSS/JavaScript (no build step required)
- Chart.js 4.x for interactive charts
- ECharts for topic relations graph
