# Radiology Topic Analysis Dashboard

An interactive web dashboard showcasing NMF-based topic modeling results from radiology imaging journals.

## Features

- **Overview**: Model statistics, coherence scores chart, t-SNE visualization
- **Topic Explorer**: Interactive grid of all 25 topics with wordclouds and top words
- **Topic Relations**: Embedded interactive ECharts graph showing topic relationships
- **Temporal Trends**: Line charts and area charts showing topic evolution over time
- **Top Documents**: Browse representative documents for each topic

## Deployment to GitHub Pages

1. Create a new repository on GitHub (e.g., `radiology-topic-analysis`)

2. Add the remote and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/radiology-topic-analysis.git
   git add .
   git commit -m "Initial commit: Topic analysis dashboard"
   git push -u origin main
   ```

3. Enable GitHub Pages:
   - Go to your repository on GitHub
   - Click **Settings** > **Pages**
   - Under "Source", select **Deploy from a branch**
   - Select **main** branch and **/ (root)** folder
   - Click **Save**

4. Your site will be available at: `https://YOUR_USERNAME.github.io/radiology-topic-analysis/`

## Local Development

To run locally, you need a local server (due to CORS restrictions for loading JSON files):

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js
npx serve .
```

Then open `http://localhost:8000` in your browser.

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
