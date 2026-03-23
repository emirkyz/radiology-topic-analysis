# Radiology Topic Analysis Dashboard

Github Pages Link : https://emirkyz.github.io/radiology-topic-analysis/

## Apps

### Radiology Imaging
- [Radiology Imaging NMTF 25 Topics](https://emirkyz.github.io/radiology-topic-analysis/radiology-imaging-nmtf-25/)

### Heart Failure
- [Heart Failure NMTF 34 Topics](https://emirkyz.github.io/radiology-topic-analysis/heart-failure-nmtf-34/)
- [Heart Failure PNMF 43 Topics](https://emirkyz.github.io/radiology-topic-analysis/heart-failure-pnmf-43/)

### Nutrition Data
- [Nutrition Data NMTF 26 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-data-nmtf-26/)
- [Nutrition Data PNMF 52 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-data-pnmf-52/)

### Nutrition Heart Failure
- [Nutrition Heart Failure NMTF 15 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-heart-failure-nmtf-15/)
- [Nutrition Heart Failure PNMF 7 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-heart-failure-pnmf-7/)
- [Nutrition Heart Failure PNMF 15 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-heart-failure-pnmf-15/)

### Nutrition Heart
- [Nutrition Heart NMTF 15 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-heart-nmtf-15/)
- [Nutrition Heart PNMF 15 Topics](https://emirkyz.github.io/radiology-topic-analysis/nutrition-heart-pnmf-15/)

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
