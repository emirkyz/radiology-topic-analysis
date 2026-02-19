#!/usr/bin/env python3
"""
Dynamic Topic Analysis App Generator

This module provides a programmatic API to generate visualization apps from
topic modeling data. It supports any topic count and auto-detects metadata
from folder names.

Usage:
    from generate_apps import generate_app, generate_all_apps

    # Generate single app from folder path
    generate_app("to_generate_from/heart_failure_with_pagerank_nmtf_bpe_34")

    # With optional output directory
    generate_app("to_generate_from/source_folder", output_dir="my-output/")

    # Generate all apps from to_generate_from folder
    generate_all_apps()

CLI Usage:
    uv run python generate_apps.py
"""

import os
import re
import json
import shutil
import csv
from pathlib import Path
from typing import Optional


# Base directory
BASE_DIR = Path(__file__).parent


def parse_folder_name(folder_name: str) -> dict:
    """
    Parse folder name to extract metadata.

    Args:
        folder_name: Folder name like 'heart_failure_with_pagerank_nmtf_bpe_34'

    Returns:
        dict with keys: dataset, method, topic_count
        Returns None if pattern doesn't match
    """
    # Pattern: {dataset}_with_pagerank_{method}_bpe_{topic_count}
    pattern = r'^(.+)_with_pagerank_(nmtf|pnmf)_bpe_(\d+)$'
    match = re.match(pattern, folder_name)

    if not match:
        return None

    return {
        "dataset": match.group(1),
        "method": match.group(2),
        "topic_count": int(match.group(3))
    }


def find_data_file(source_dir: Path, prefix: str) -> Optional[Path]:
    """
    Find the main data file (coherence_scores or relevance_top_words).

    Args:
        source_dir: Source directory path
        prefix: File prefix like 'heart_failure_with_pagerank_nmtf_bpe_34'

    Returns:
        Path to data file or None
    """
    # Try coherence_scores.json first (25-topic format)
    coherence_file = source_dir / f"{prefix}_coherence_scores.json"
    if coherence_file.exists():
        return coherence_file

    # Try relevance_top_words.json (34/43-topic format)
    relevance_file = source_dir / f"{prefix}_relevance_top_words.json"
    if relevance_file.exists():
        return relevance_file

    return None


def load_topic_data(data_file: Path) -> dict:
    """
    Load and normalize topic data from either file format.

    Args:
        data_file: Path to coherence_scores.json or relevance_top_words.json

    Returns:
        Normalized data dict with 'relevance' and 'gensim' keys
    """
    with open(data_file, 'r') as f:
        data = json.load(f)

    return data


def get_topic_count(data: dict) -> int:
    """
    Auto-detect topic count from data.

    Args:
        data: Loaded topic data

    Returns:
        Number of topics
    """
    # Try from relevance keys
    if 'relevance' in data:
        return len(data['relevance'])

    # Try from gensim c_v_per_topic
    if 'gensim' in data and 'c_v_per_topic' in data['gensim']:
        return len(data['gensim']['c_v_per_topic'])

    return 0


def generate_output_dir_name(metadata: dict) -> str:
    """
    Generate output directory name from metadata.

    Args:
        metadata: Dict with dataset, method, topic_count

    Returns:
        Output dir name like 'heart-failure-nmtf-34'
    """
    dataset = metadata['dataset'].replace('_', '-')
    method = metadata['method']
    topic_count = metadata['topic_count']
    return f"{dataset}-{method}-{topic_count}"


# =============================================================================
# CSS Content
# =============================================================================
CSS_CONTENT = '''\
/* CSS Variables */
:root {
    --primary-color: #2563eb;
    --primary-dark: #1d4ed8;
    --secondary-color: #7c3aed;
    --background: #f8fafc;
    --card-bg: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --radius: 12px;
    --radius-sm: 8px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: var(--background);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}

.header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
.header .subtitle { font-size: 1.1rem; opacity: 0.9; }

.nav-tabs {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-tab {
    padding: 0.75rem 1.5rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all 0.2s ease;
}

.nav-tab:hover { background: var(--background); color: var(--text-primary); }
.nav-tab.active { background: var(--primary-color); color: white; }

.main-content { max-width: 1400px; margin: 0 auto; padding: 2rem; }

.section { display: none; }
.section.active { display: block; }

.section-header { margin-bottom: 2rem; }
.section-header h2 { font-size: 1.75rem; color: var(--text-primary); margin-bottom: 0.5rem; }
.section-header p { color: var(--text-secondary); }

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
}

.stat-value { font-size: 2.5rem; font-weight: 700; color: var(--primary-color); margin-bottom: 0.5rem; }
.stat-label { color: var(--text-secondary); font-size: 0.9rem; }

.charts-row { margin-bottom: 2rem; }

.chart-container {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.chart-container h3 { margin-bottom: 1rem; color: var(--text-primary); }
.chart-container canvas { width: 100% !important; height: 400px !important; }

.visualizations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
}

.viz-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.viz-card h3 { margin-bottom: 1rem; color: var(--text-primary); }

.viz-image {
    width: 100%;
    height: auto;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: transform 0.2s ease;
}

.viz-image:hover { transform: scale(1.02); }

.topics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
}

.topic-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s ease;
}

.topic-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }

.topic-card-header {
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
}

.topic-number { font-weight: 700; color: var(--primary-color); }

.coherence-badge {
    background: var(--success-color);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.coherence-badge.low { background: var(--warning-color); }

.topic-wordcloud { width: 100%; height: 180px; object-fit: contain; background: #f1f5f9; }

.topic-words { padding: 1rem; }
.topic-words-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }

.word-tag {
    background: var(--background);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.graph-container {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.graph-container iframe { width: 100%; height: 700px; border: none; }

.open-fullscreen {
    display: inline-block;
    margin-top: 0.5rem;
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
}

.open-fullscreen:hover { text-decoration: underline; }

.temporal-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }

.temporal-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.temporal-card.full-width { grid-column: 1 / -1; }
.temporal-card h3 { margin-bottom: 1rem; color: var(--text-primary); }

.temporal-image {
    width: 100%;
    height: auto;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: transform 0.2s ease;
}

.temporal-image:hover { transform: scale(1.02); }

.documents-controls { margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.documents-controls label { font-weight: 500; }

.documents-controls select {
    padding: 0.75rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    font-size: 1rem;
    min-width: 300px;
    cursor: pointer;
}

.documents-list { display: flex; flex-direction: column; gap: 1rem; }

.document-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.document-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.document-id { font-weight: 600; color: var(--text-secondary); }

.document-score {
    background: var(--primary-color);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
}

.document-text {
    color: var(--text-primary);
    line-height: 1.7;
    max-height: 150px;
    overflow: hidden;
    position: relative;
}

.document-text::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40px;
    background: linear-gradient(transparent, var(--card-bg));
}

.document-text.expanded { max-height: none; }
.document-text.expanded::after { display: none; }

.expand-btn {
    margin-top: 0.5rem;
    background: none;
    border: none;
    color: var(--primary-color);
    cursor: pointer;
    font-weight: 500;
}

.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.modal.active { display: flex; }

.modal-content {
    background: var(--card-bg);
    border-radius: var(--radius);
    max-width: 900px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
}

.modal-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: var(--text-secondary);
    line-height: 1;
}

.modal-close:hover { color: var(--text-primary); }

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.modal-header h2 { font-size: 1.5rem; }

.modal-body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
}

.modal-wordcloud img { width: 100%; border-radius: var(--radius-sm); }
.modal-words h3 { margin-bottom: 1rem; }

.words-table { width: 100%; border-collapse: collapse; }

.words-table th,
.words-table td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.words-table th { font-weight: 600; color: var(--text-secondary); font-size: 0.85rem; }

.lightbox {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    z-index: 2000;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.lightbox.active { display: flex; }
.lightbox img { max-width: 95%; max-height: 95%; object-fit: contain; }

.footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
    border-top: 1px solid var(--border-color);
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .header h1 { font-size: 1.5rem; }
    .nav-tabs { gap: 0.25rem; }
    .nav-tab { padding: 0.5rem 1rem; font-size: 0.85rem; }
    .main-content { padding: 1rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .stat-value { font-size: 1.75rem; }
    .visualizations-grid { grid-template-columns: 1fr; }
    .temporal-grid { grid-template-columns: 1fr; }
    .modal-body { grid-template-columns: 1fr; }
    .documents-controls { flex-direction: column; align-items: flex-start; }
    .documents-controls select { min-width: 100%; }
    .graph-container iframe { height: 500px; }
}

.loading { text-align: center; padding: 2rem; color: var(--text-secondary); }

.loading::after {
    content: '';
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-left: 0.5rem;
    vertical-align: middle;
}

@keyframes spin { to { transform: rotate(360deg); } }
'''


# =============================================================================
# JavaScript Content - topics.js
# =============================================================================
TOPICS_JS = '''\
/**
 * Topic Data Handler
 */

const TopicData = {
    coherenceData: null,
    diversityData: null,
    topDocsData: null,

    async loadAll() {
        try {
            const [coherence, topDocs] = await Promise.all([
                this.loadJSON('data/coherence_scores.json'),
                this.loadJSON('data/top_docs.json')
            ]);

            this.coherenceData = coherence;
            this.topDocsData = topDocs;

            // Try to load diversity scores (may not exist)
            try {
                this.diversityData = await this.loadJSON('data/diversity_scores.json');
            } catch (e) {
                console.log('Diversity scores not available');
                this.diversityData = null;
            }

            return true;
        } catch (error) {
            console.error('Error loading data:', error);
            return false;
        }
    },

    async loadJSON(path) {
        const response = await fetch(path);
        if (!response.ok) throw new Error(`Failed to load ${path}`);
        return response.json();
    },

    getTopicCount() {
        // Try from relevance keys first
        if (this.coherenceData?.relevance) {
            return Object.keys(this.coherenceData.relevance).length;
        }
        // Fall back to gensim
        if (this.coherenceData?.gensim?.c_v_per_topic) {
            return Object.keys(this.coherenceData.gensim.c_v_per_topic).length;
        }
        return 0;
    },

    getAverageCoherence() {
        return this.coherenceData?.gensim?.c_v_average || 0;
    },

    getCoherenceScores() {
        if (!this.coherenceData?.gensim?.c_v_per_topic) return [];

        return Object.entries(this.coherenceData.gensim.c_v_per_topic).map(([topic, score]) => {
            // Handle both "Topic 1" and "topic_01" formats
            let topicNum;
            if (topic.startsWith('topic_')) {
                topicNum = parseInt(topic.replace('topic_', ''));
            } else {
                topicNum = parseInt(topic.replace('Topic ', ''));
            }
            return {
                topic: `Topic ${topicNum}`,
                topicNum: topicNum,
                score: score
            };
        }).sort((a, b) => a.topicNum - b.topicNum);
    },

    getDiversityMetrics() {
        if (!this.diversityData) return null;

        return {
            proportionUnique: this.diversityData.proportion_unique_words,
            avgJaccard: this.diversityData.average_jaccard_diversity,
            overallScore: this.diversityData.diversity_summary?.overall_diversity_score,
            uniqueWords: this.diversityData.diversity_summary?.total_unique_words
        };
    },

    getTopWords(topicNum, limit = 30) {
        const topicKey = `topic_${String(topicNum).padStart(2, '0')}`;

        if (!this.coherenceData?.relevance?.[topicKey]) return [];

        return Object.entries(this.coherenceData.relevance[topicKey])
            .map(([word, score]) => ({
                word: word.replace(/_/g, ' '),
                score: score
            }))
            .slice(0, limit);
    },

    getTopDocuments(topicNum, limit = 10) {
        const topicKey = `Topic ${topicNum}`;

        if (!this.topDocsData?.[topicKey]) return [];

        return Object.entries(this.topDocsData[topicKey])
            .map(([docId, content]) => {
                const parts = content.split(':');
                const score = parseFloat(parts[parts.length - 1]) || 0;
                const text = parts.slice(0, -1).join(':');

                return { id: docId, text: text, score: score };
            })
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    },

    getTopicSummaries() {
        const coherenceScores = this.getCoherenceScores();

        return coherenceScores.map(({ topic, topicNum, score }) => {
            const topWords = this.getTopWords(topicNum, 5);

            return {
                topic: topic,
                topicNum: topicNum,
                coherence: score,
                topWords: topWords,
                wordcloudPath: `images/wordclouds/Topic ${String(topicNum).padStart(2, '0')}.png`
            };
        });
    },

    generateTopicLabel(topicNum) {
        const topWords = this.getTopWords(topicNum, 3);
        if (topWords.length === 0) return `Topic ${topicNum}`;
        return topWords.map(w => w.word).join(', ');
    }
};

window.TopicData = TopicData;
'''


# =============================================================================
# JavaScript Content - charts.js (dynamic for any topic count)
# =============================================================================
def generate_charts_js(topic_count: int) -> str:
    """Generate charts.js with dynamic color palette for any topic count."""
    # Generate enough colors for any topic count
    base_colors = [
        '#2563eb', '#7c3aed', '#db2777', '#dc2626', '#ea580c',
        '#d97706', '#ca8a04', '#65a30d', '#16a34a', '#059669',
        '#0d9488', '#0891b2', '#0284c7', '#2563eb', '#4f46e5',
        '#7c3aed', '#9333ea', '#c026d3', '#db2777', '#e11d48',
        '#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e',
        '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6', '#6366f1',
        '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e',
        '#fb7185', '#fda4af', '#fecdd3', '#ffe4e6', '#fecaca',
        '#fed7aa', '#fef08a', '#d9f99d', '#bbf7d0', '#99f6e4'
    ]

    # Extend colors if needed
    while len(base_colors) < topic_count:
        base_colors.extend(base_colors)

    colors_json = json.dumps(base_colors[:max(topic_count, 25)])

    return f'''\
/**
 * Chart.js Configurations
 */

const Charts = {{
    coherenceChart: null,

    colors: {colors_json},

    init() {{
        this.initCoherenceChart();
    }},

    initCoherenceChart() {{
        const ctx = document.getElementById('coherence-chart');
        if (!ctx) return;

        const scores = TopicData.getCoherenceScores();

        const data = {{
            labels: scores.map(s => `Topic ${{s.topicNum}}`),
            datasets: [{{
                label: 'Coherence Score (C_V)',
                data: scores.map(s => s.score),
                backgroundColor: scores.map((_, i) => this.colors[i % this.colors.length]),
                borderColor: scores.map((_, i) => this.colors[i % this.colors.length]),
                borderWidth: 1,
                borderRadius: 4,
                barThickness: Math.max(8, Math.min(20, 500 / scores.length))
            }}]
        }};

        const averageCoherence = TopicData.getAverageCoherence();

        const config = {{
            type: 'bar',
            data: data,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return `Coherence: ${{context.raw.toFixed(4)}}`;
                            }},
                            afterLabel: function(context) {{
                                const topicNum = context.dataIndex + 1;
                                const topWords = TopicData.getTopWords(topicNum, 3);
                                return `Top words: ${{topWords.map(w => w.word).join(', ')}}`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ maxRotation: 45, minRotation: 45 }}
                    }},
                    y: {{
                        beginAtZero: false,
                        min: 0.4,
                        max: 1.0,
                        grid: {{ color: '#e2e8f0' }},
                        title: {{ display: true, text: 'Coherence Score (C_V)' }}
                    }}
                }},
                onClick: (event, elements) => {{
                    if (elements.length > 0) {{
                        const index = elements[0].index;
                        const topicNum = index + 1;
                        showTopicModal(topicNum);
                    }}
                }}
            }}
        }};

        this.coherenceChart = new Chart(ctx, config);
    }},

    getTopicColor(topicNum) {{
        return this.colors[(topicNum - 1) % this.colors.length];
    }},

    destroy() {{
        if (this.coherenceChart) {{
            this.coherenceChart.destroy();
            this.coherenceChart = null;
        }}
    }}
}};

window.Charts = Charts;
'''


# =============================================================================
# JavaScript Content - app.js
# =============================================================================
APP_JS = '''\
/**
 * Main Application Logic
 */

let currentSection = 'overview';
let currentTopic = 1;

async function init() {
    showLoading(true);

    const success = await TopicData.loadAll();

    if (!success) {
        showError('Failed to load data. Please refresh the page.');
        return;
    }

    initNavigation();
    initOverview();
    initTopicsGrid();
    initDocumentsSection();
    Charts.init();
    showLoading(false);
}

function showLoading(show) {
    console.log(show ? 'Loading...' : 'Loaded');
}

function showError(message) {
    const main = document.querySelector('.main-content');
    main.innerHTML = `<div class="error-message" style="text-align: center; padding: 2rem; color: #dc2626;">${message}</div>`;
}

function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const section = tab.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(sectionId) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.section === sectionId);
    });
    document.querySelectorAll('.section').forEach(section => {
        section.classList.toggle('active', section.id === sectionId);
    });
    currentSection = sectionId;
}

function initOverview() {
    document.getElementById('total-topics').textContent = TopicData.getTopicCount();
    document.getElementById('avg-coherence').textContent = TopicData.getAverageCoherence().toFixed(3);

    const diversity = TopicData.getDiversityMetrics();
    if (diversity && diversity.overallScore) {
        document.getElementById('diversity-score').textContent = (diversity.overallScore * 100).toFixed(1) + '%';
        document.getElementById('unique-words').textContent = diversity.uniqueWords?.toLocaleString() || '-';
    } else {
        document.getElementById('diversity-score').textContent = 'N/A';
        document.getElementById('unique-words').textContent = 'N/A';
    }
}

function initTopicsGrid() {
    const grid = document.getElementById('topics-grid');
    if (!grid) return;

    const summaries = TopicData.getTopicSummaries();

    grid.innerHTML = summaries.map(topic => `
        <div class="topic-card" onclick="showTopicModal(${topic.topicNum})" data-topic="${topic.topicNum}">
            <div class="topic-card-header">
                <span class="topic-number">Topic ${topic.topicNum}</span>
                <span class="coherence-badge ${topic.coherence < 0.6 ? 'low' : ''}">${topic.coherence.toFixed(3)}</span>
            </div>
            <img
                src="${topic.wordcloudPath}"
                alt="Topic ${topic.topicNum} Wordcloud"
                class="topic-wordcloud"
                loading="lazy"
            >
            <div class="topic-words">
                <div class="topic-words-list">
                    ${topic.topWords.slice(0, 5).map(w => `<span class="word-tag">${w.word}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function initDocumentsSection() {
    const select = document.getElementById('topic-select');
    if (!select) return;

    const topicCount = TopicData.getTopicCount();

    select.innerHTML = '';
    for (let i = 1; i <= topicCount; i++) {
        const topWords = TopicData.getTopWords(i, 3);
        const label = topWords.map(w => w.word).join(', ');

        const option = document.createElement('option');
        option.value = i;
        option.textContent = `Topic ${i}: ${label}`;
        select.appendChild(option);
    }

    select.addEventListener('change', () => {
        loadDocuments(parseInt(select.value));
    });

    loadDocuments(1);
}

function loadDocuments(topicNum) {
    const container = document.getElementById('documents-list');
    if (!container) return;

    const docs = TopicData.getTopDocuments(topicNum);

    if (docs.length === 0) {
        container.innerHTML = '<p class="no-docs">No documents available for this topic.</p>';
        return;
    }

    container.innerHTML = docs.map((doc, index) => `
        <div class="document-card">
            <div class="document-header">
                <span class="document-id">#${index + 1} (ID: ${doc.id})</span>
                <span class="document-score">Score: ${doc.score.toFixed(4)}</span>
            </div>
            <div class="document-text" id="doc-text-${index}">
                ${formatDocumentText(doc.text)}
            </div>
            <button class="expand-btn" onclick="toggleDocumentExpand(${index})">Show more</button>
        </div>
    `).join('');
}

function formatDocumentText(text) {
    return text.replace(/\\s+/g, ' ').trim().split(' ').slice(0, 100).join(' ');
}

function toggleDocumentExpand(index) {
    const textEl = document.getElementById(`doc-text-${index}`);
    const btn = textEl.nextElementSibling;

    if (textEl.classList.contains('expanded')) {
        textEl.classList.remove('expanded');
        btn.textContent = 'Show more';
    } else {
        textEl.classList.add('expanded');
        btn.textContent = 'Show less';
    }
}

function showTopicModal(topicNum) {
    const modal = document.getElementById('topic-modal');
    if (!modal) return;

    const topWords = TopicData.getTopWords(topicNum);
    const coherenceScores = TopicData.getCoherenceScores();
    const coherence = coherenceScores.find(s => s.topicNum === topicNum)?.score || 0;

    document.getElementById('modal-title').textContent = `Topic ${topicNum}`;
    document.getElementById('modal-coherence').textContent = `C_V: ${coherence.toFixed(3)}`;
    document.getElementById('modal-coherence').className = `coherence-badge ${coherence < 0.6 ? 'low' : ''}`;
    document.getElementById('modal-wordcloud-img').src = `images/wordclouds/Topic ${String(topicNum).padStart(2, '0')}.png`;

    const tbody = document.querySelector('#modal-words-table tbody');
    tbody.innerHTML = topWords.map(word => `
        <tr>
            <td>${word.word}</td>
            <td>${word.score.toFixed(4)}</td>
        </tr>
    `).join('');

    modal.classList.add('active');
    currentTopic = topicNum;
}

function closeModal() {
    const modal = document.getElementById('topic-modal');
    if (modal) modal.classList.remove('active');
}

function openLightbox(img) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');

    if (lightbox && lightboxImg) {
        lightboxImg.src = img.src;
        lightbox.classList.add('active');
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) lightbox.classList.remove('active');
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeLightbox();
    }
});

document.getElementById('topic-modal')?.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) closeModal();
});

document.addEventListener('DOMContentLoaded', init);
'''


def generate_index_html(method_upper: str, topic_count: int, dataset_title: str, has_violin_plot: bool = False, has_umap: bool = False) -> str:
    """Generate index.html content with dynamic topic count."""
    # Conditionally add violin plot tab
    violin_tab = '<button class="nav-tab" data-section="violin">Interactive Violin Plot</button>' if has_violin_plot else ''

    # Conditionally add violin plot section
    violin_section = '''
        <section id="violin" class="section">
            <div class="section-header">
                <h2>Interactive Violin Plot</h2>
                <p>Topic distribution by year - hover over violins for details</p>
                <a href="violin-plot.html" target="_blank" class="open-fullscreen">Open in Full Screen</a>
            </div>
            <div class="graph-container">
                <iframe src="violin-plot.html" id="violin-plot-iframe" title="Interactive Violin Plot"></iframe>
            </div>
        </section>
''' if has_violin_plot else ''

    # Conditionally add UMAP visualization card
    umap_card = '''
                <div class="viz-card">
                    <h3>UMAP Visualization</h3>
                    <img src="images/umap.png" alt="UMAP Visualization" class="viz-image" onclick="openLightbox(this)">
                </div>
''' if has_umap else ''

    return f'''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dataset_title} Topic Analysis - {method_upper}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header class="header">
        <div class="header-content">
            <h1>{dataset_title} Topic Analysis</h1>
            <p class="subtitle">{method_upper}-based Topic Modeling Results ({topic_count} Topics)</p>
        </div>
    </header>

    <nav class="nav-tabs">
        <button class="nav-tab active" data-section="overview">Overview</button>
        <button class="nav-tab" data-section="topics">Topic Explorer</button>
        <button class="nav-tab" data-section="graph">Interactive Temporal Graph</button>
        {violin_tab}
        <button class="nav-tab" data-section="temporal">Temporal Trends</button>
        <button class="nav-tab" data-section="documents">Top Documents</button>
    </nav>

    <main class="main-content">
        <section id="overview" class="section active">
            <div class="section-header">
                <h2>Model Overview</h2>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="total-topics">{topic_count}</div>
                    <div class="stat-label">Topics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avg-coherence">-</div>
                    <div class="stat-label">Avg. Coherence (C_V)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="diversity-score">-</div>
                    <div class="stat-label">Diversity Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="unique-words">-</div>
                    <div class="stat-label">Unique Words</div>
                </div>
            </div>

            <div class="charts-row">
                <div class="chart-container">
                    <h3>Topic Coherence Scores (C_V)</h3>
                    <canvas id="coherence-chart"></canvas>
                </div>
            </div>

            <div class="visualizations-grid">
                <div class="viz-card">
                    <h3>t-SNE Visualization</h3>
                    <img src="images/tsne.png" alt="t-SNE Visualization" class="viz-image" onclick="openLightbox(this)">
                </div>
{umap_card}
                <div class="viz-card">
                    <h3>Document Distribution</h3>
                    <img src="images/document_dist.png" alt="Document Distribution" class="viz-image" onclick="openLightbox(this)">
                </div>
            </div>
        </section>

        <section id="topics" class="section">
            <div class="section-header">
                <h2>Topic Explorer</h2>
                <p>Click on any topic card to see detailed information</p>
            </div>
            <div class="topics-grid" id="topics-grid"></div>
        </section>

        <section id="graph" class="section">
            <div class="section-header">
                <h2>Interactive Topic Temporal Line Graph</h2>
                <p>Interactive visualization of topic temporal changes</p>
                <a href="topic-graph.html" target="_blank" class="open-fullscreen">Open in Full Screen</a>
            </div>
            <div class="graph-container">
                <iframe src="topic-graph.html" id="topic-graph-iframe" title="Interactive Topic Temporal Line Graph"></iframe>
            </div>
        </section>
{violin_section}
        <section id="temporal" class="section">
            <div class="section-header">
                <h2>Temporal Trends</h2>
                <p>Topic distribution over time</p>
            </div>

            <div class="temporal-grid">
                <div class="temporal-card">
                    <h3>Quarterly Trends (Line Chart)</h3>
                    <img src="images/temporal_line.png" alt="Temporal Line Chart" class="temporal-image" onclick="openLightbox(this)">
                </div>
                <div class="temporal-card">
                    <h3>Quarterly Trends (Stacked Area)</h3>
                    <img src="images/temporal_area.png" alt="Temporal Stacked Area Chart" class="temporal-image" onclick="openLightbox(this)">
                </div>
                <div class="temporal-card full-width">
                    <h3>Yearly Distribution</h3>
                    <img src="images/yearly_dist.png" alt="Yearly Distribution" class="temporal-image" onclick="openLightbox(this)">
                </div>
            </div>
        </section>

        <section id="documents" class="section">
            <div class="section-header">
                <h2>Top Documents</h2>
                <p>Representative documents for each topic</p>
            </div>

            <div class="documents-controls">
                <label for="topic-select">Select Topic:</label>
                <select id="topic-select"></select>
            </div>

            <div class="documents-list" id="documents-list"></div>
        </section>
    </main>

    <div class="modal" id="topic-modal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">&times;</button>
            <div class="modal-header">
                <h2 id="modal-title">Topic Details</h2>
                <span class="coherence-badge" id="modal-coherence"></span>
            </div>
            <div class="modal-body">
                <div class="modal-wordcloud">
                    <img id="modal-wordcloud-img" src="" alt="Wordcloud">
                </div>
                <div class="modal-words">
                    <h3>Top Words</h3>
                    <table class="words-table" id="modal-words-table">
                        <thead>
                            <tr>
                                <th>Word</th>
                                <th>Relevance Score</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <img id="lightbox-img" src="" alt="Enlarged view">
    </div>

    <footer class="footer">
        <p>Generated with {method_upper} Topic Modeling | {dataset_title} Research Analysis | {topic_count} Topics</p>
    </footer>

    <script src="js/topics.js"></script>
    <script src="js/charts.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
'''


def generate_topic_graph_html(csv_path: Path, method_upper: str, topic_count: int) -> str:
    """Generate topic-graph.html content with embedded CSV data."""
    # Read CSV data
    csv_data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_data.append(row)

    # Convert to JSON string
    csv_json = json.dumps(csv_data, indent=2)

    return f'''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Topic Temporal Graph - {method_upper}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
            color: #1e293b;
        }}

        .header {{
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{ font-size: 1.5rem; font-weight: 600; }}
        .header p {{ opacity: 0.9; font-size: 0.9rem; }}

        .controls {{
            background: #ffffff;
            padding: 1rem 2rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}

        .control-group {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .control-group label {{
            font-weight: 500;
            color: #64748b;
            font-size: 0.9rem;
        }}

        .topic-dropdown {{
            position: relative;
        }}

        .topic-dropdown-btn {{
            padding: 0.5rem 1rem;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            color: #1e293b;
            font-size: 0.9rem;
            min-width: 200px;
            cursor: pointer;
            text-align: left;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.5rem;
        }}

        .topic-dropdown-btn:hover {{ background: #e2e8f0; }}

        .topic-dropdown-panel {{
            display: none;
            position: absolute;
            top: calc(100% + 4px);
            left: 0;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 100;
            max-height: 280px;
            overflow-y: auto;
            min-width: 220px;
        }}

        .topic-dropdown-panel.open {{ display: block; }}

        .topic-checkbox-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.75rem;
            cursor: pointer;
            font-size: 0.875rem;
            color: #1e293b;
            user-select: none;
        }}

        .topic-checkbox-item:hover {{ background: #f1f5f9; }}

        .topic-checkbox-item input[type="checkbox"] {{
            cursor: pointer;
            width: 14px;
            height: 14px;
        }}

        .quick-btn {{
            padding: 0.5rem 1rem;
            background: #2563eb;
            border: none;
            border-radius: 6px;
            color: #fff;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
        }}

        .quick-btn:hover {{ background: #1d4ed8; }}

        .quick-btn.secondary {{
            background: #f1f5f9;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }}

        .quick-btn.secondary:hover {{
            background: #e2e8f0;
            color: #1e293b;
        }}

        .selected-topics {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            flex: 1;
        }}

        .topic-tag {{
            background: #e0e7ff;
            color: #3730a3;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .topic-tag .remove {{
            cursor: pointer;
            opacity: 0.7;
            font-weight: bold;
        }}

        .topic-tag .remove:hover {{ opacity: 1; }}

        .chart-container {{
            width: 100%;
            height: calc(100vh - 140px);
            padding: 1rem;
        }}

        #chart {{
            width: 100%;
            height: 100%;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}

        .no-selection {{
            color: #64748b;
            font-size: 0.85rem;
        }}

        @media (max-width: 768px) {{
            .controls {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .topic-dropdown-btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Topic Temporal Distribution</h1>
            <p>{method_upper} Analysis - {topic_count} Topics</p>
        </div>
    </div>

    <div class="controls">
        <div class="control-group">
            <label>Topics:</label>
            <div class="topic-dropdown" id="topicDropdown">
                <button class="topic-dropdown-btn" id="dropdownBtn" onclick="toggleDropdown()">
                    <span id="dropdownLabel">All Topics</span>
                    <span>▾</span>
                </button>
                <div class="topic-dropdown-panel" id="dropdownPanel">
                    <div id="topicCheckboxList"></div>
                </div>
            </div>
        </div>

        <div class="control-group">
            <button class="quick-btn" onclick="selectAll()">Select All</button>
            <button class="quick-btn secondary" onclick="clearAll()">Clear All</button>
        </div>

        <div class="selected-topics" id="selectedTopics">
        </div>
    </div>

    <div class="chart-container">
        <div id="chart"></div>
    </div>

    <script>
    // Embedded CSV data
    const csvData = {csv_json};

    // Get all topic columns
    const allTopics = Object.keys(csvData[0]).filter(key => key.startsWith('Topic'));

    // Initialize
    let selectedTopics = [];
    let chart = null;

    // Color palette (extended for more topics)
    const colors = [
        '#2563eb', '#7c3aed', '#db2777', '#dc2626', '#ea580c',
        '#d97706', '#ca8a04', '#65a30d', '#16a34a', '#059669',
        '#0d9488', '#0891b2', '#0284c7', '#4f46e5', '#9333ea',
        '#c026d3', '#e11d48', '#ef4444', '#f97316', '#eab308',
        '#84cc16', '#22c55e', '#14b8a6', '#06b6d4', '#0ea5e9',
        '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
        '#ec4899', '#f43f5e', '#fb7185', '#f472b6', '#e879f9',
        '#c084fc', '#a78bfa', '#818cf8', '#60a5fa', '#38bdf8',
        '#22d3ee', '#2dd4bf', '#34d399', '#4ade80', '#a3e635'
    ];

    // Initialize the chart
    document.addEventListener('DOMContentLoaded', function() {{
        chart = echarts.init(document.getElementById('chart'));

        // Populate topic checkboxes
        const checkboxList = document.getElementById('topicCheckboxList');
        allTopics.forEach(topic => {{
            const item = document.createElement('label');
            item.className = 'topic-checkbox-item';
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.value = topic;
            cb.id = 'cb_' + topic.replace(/\s/g, '_');
            cb.checked = true;
            cb.addEventListener('change', function() {{
                if (this.checked) {{
                    if (!selectedTopics.includes(topic)) selectedTopics.push(topic);
                }} else {{
                    selectedTopics = selectedTopics.filter(t => t !== topic);
                }}
                updateDropdownLabel();
                updateSelectedTopicTags();
                updateChart();
            }});
            const span = document.createElement('span');
            span.textContent = topic;
            item.appendChild(cb);
            item.appendChild(span);
            checkboxList.appendChild(item);
        }});

        // Select all topics by default
        selectedTopics = [...allTopics];

        updateDropdownLabel();
        updateSelectedTopicTags();
        updateChart();

        window.addEventListener('resize', () => chart.resize());
    }});

    // Update the chart
    function updateChart() {{
        if (!chart || !csvData) return;

        const periods = csvData.map(row => row.period);

        const series = selectedTopics.map((topic, index) => ({{
            name: topic,
            type: 'line',
            data: csvData.map(row => parseFloat(row[topic]) || 0),
            smooth: true,
            lineStyle: {{ width: 2 }},
            itemStyle: {{ color: colors[index % colors.length] }},
            emphasis: {{
                focus: 'series',
                lineStyle: {{ width: 3 }}
            }},
            blur: {{
                lineStyle: {{ opacity: 0.2 }},
                itemStyle: {{ opacity: 0.2 }}
            }}
        }}));

        const option = {{
            title: {{
                text: selectedTopics.length === 0 ? 'Select topics to display' : 'Topic Distribution Over Time',
                left: 'center',
                top: selectedTopics.length === 0 ? 'center' : 10,
                textStyle: {{ color: '#1e293b' }}
            }},
            tooltip: {{
                trigger: 'item',
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                textStyle: {{ color: '#1e293b' }},
                formatter: function(param) {{
                    return `${{param.name}}<br/><span style="color:${{param.color}}">●</span> ${{param.seriesName}}: ${{parseFloat(param.value).toFixed(2)}}`;
                }}
            }},
            legend: {{
                data: selectedTopics,
                top: 40,
                type: 'scroll',
                textStyle: {{ color: '#64748b' }}
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: selectedTopics.length === 0 ? '50%' : 100,
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: periods,
                axisLabel: {{ rotate: 45, color: '#64748b' }},
                axisLine: {{ lineStyle: {{ color: '#e2e8f0' }} }},
                splitLine: {{ lineStyle: {{ color: '#f1f5f9' }} }}
            }},
            yAxis: {{
                type: 'value',
                name: 'Topic Weight',
                nameTextStyle: {{ color: '#64748b' }},
                axisLabel: {{ color: '#64748b' }},
                axisLine: {{ lineStyle: {{ color: '#e2e8f0' }} }},
                splitLine: {{ lineStyle: {{ color: '#f1f5f9' }} }}
            }},
            series: series
        }};

        chart.setOption(option, true);
    }}

    // Update selected topic tags display
    function updateSelectedTopicTags() {{
        const container = document.getElementById('selectedTopics');
        if (selectedTopics.length === 0) {{
            container.innerHTML = '<span class="no-selection">No topics selected</span>';
            return;
        }}

        container.innerHTML = selectedTopics.map(topic => `
            <div class="topic-tag">
                <span>${{topic}}</span>
                <span class="remove" onclick="removeTopic('${{topic}}')">×</span>
            </div>
        `).join('');
    }}

    // Remove topic from selection
    function removeTopic(topic) {{
        selectedTopics = selectedTopics.filter(t => t !== topic);
        const cb = document.getElementById('cb_' + topic.replace(/\s/g, '_'));
        if (cb) cb.checked = false;
        updateDropdownLabel();
        updateSelectedTopicTags();
        updateChart();
    }}

    // Dropdown toggle
    function toggleDropdown() {{
        document.getElementById('dropdownPanel').classList.toggle('open');
    }}

    // Close dropdown on outside click
    document.addEventListener('click', function(e) {{
        const dropdown = document.getElementById('topicDropdown');
        if (dropdown && !dropdown.contains(e.target)) {{
            document.getElementById('dropdownPanel').classList.remove('open');
        }}
    }});

    // Update dropdown button label
    function updateDropdownLabel() {{
        const label = document.getElementById('dropdownLabel');
        if (selectedTopics.length === 0) {{
            label.textContent = 'No topics selected';
        }} else if (selectedTopics.length === allTopics.length) {{
            label.textContent = 'All Topics';
        }} else {{
            label.textContent = selectedTopics.length + ' topic' + (selectedTopics.length > 1 ? 's' : '') + ' selected';
        }}
    }}

    // Select all topics
    function selectAll() {{
        selectedTopics = [...allTopics];
        document.querySelectorAll('#topicCheckboxList input[type="checkbox"]').forEach(cb => cb.checked = true);
        updateDropdownLabel();
        updateSelectedTopicTags();
        updateChart();
    }}

    // Clear all topics
    function clearAll() {{
        selectedTopics = [];
        document.querySelectorAll('#topicCheckboxList input[type="checkbox"]').forEach(cb => cb.checked = false);
        updateDropdownLabel();
        updateSelectedTopicTags();
        updateChart();
    }}
    </script>
</body>
</html>
'''


def generate_app(source_folder: str, output_dir: str = None,
                 prefix: str = None, method: str = None,
                 dataset: str = None) -> str:
    """
    Generate a visualization app from a source folder.

    Args:
        source_folder: Path to folder (e.g., "to_generate_from/heart_failure_with_pagerank_nmtf_bpe_34")
        output_dir: Optional output directory (auto-generated if not provided)

    Returns:
        Path to generated app directory
    """
    source_path = Path(source_folder)
    if not source_path.is_absolute():
        source_path = BASE_DIR / source_folder

    if not source_path.exists():
        raise FileNotFoundError(f"Source folder not found: {source_path}")

    # Parse folder name for metadata
    folder_name = source_path.name

    if prefix and method and dataset:
        metadata = {"dataset": dataset, "method": method, "topic_count": 0}
    else:
        metadata = parse_folder_name(folder_name)
        if not metadata:
            raise ValueError(f"Invalid folder name format: {folder_name}")
        prefix = folder_name

    data_file = find_data_file(source_path, prefix)

    if not data_file:
        raise FileNotFoundError(f"No data file found in {source_path}")

    topic_data = load_topic_data(data_file)
    topic_count = get_topic_count(topic_data)

    if topic_count == 0:
        raise ValueError(f"Could not determine topic count from data")

    # Update metadata with actual topic count from data
    metadata['topic_count'] = topic_count

    # Generate output directory
    if output_dir:
        output_path = Path(output_dir)
        if not output_path.is_absolute():
            output_path = BASE_DIR / output_dir
    else:
        output_path = BASE_DIR / generate_output_dir_name(metadata)

    method_upper = metadata['method'].upper()
    dataset_title = metadata['dataset'].replace('_', ' ').title()

    print(f"\n{'='*60}")
    print(f"Creating {method_upper} app ({topic_count} topics) in {output_path}")
    print('='*60)

    # Create directory structure
    (output_path / "css").mkdir(parents=True, exist_ok=True)
    (output_path / "js").mkdir(parents=True, exist_ok=True)
    (output_path / "data").mkdir(parents=True, exist_ok=True)
    (output_path / "images" / "wordclouds").mkdir(parents=True, exist_ok=True)

    # Write CSS
    print("  Writing CSS...")
    (output_path / "css" / "styles.css").write_text(CSS_CONTENT)

    # Write JavaScript files
    print("  Writing JavaScript files...")
    (output_path / "js" / "topics.js").write_text(TOPICS_JS)
    (output_path / "js" / "charts.js").write_text(generate_charts_js(topic_count))
    (output_path / "js" / "app.js").write_text(APP_JS)

    # Copy data files
    print("  Copying data files...")

    # Main coherence/relevance data file
    shutil.copy(data_file, output_path / "data" / "coherence_scores.json")

    # Diversity scores (optional)
    diversity_src = source_path / f"{prefix}_diversity_scores.json"
    if diversity_src.exists():
        shutil.copy(diversity_src, output_path / "data" / "diversity_scores.json")

    # Top docs
    topdocs_src = source_path / f"{prefix}_top_docs.json"
    if topdocs_src.exists():
        shutil.copy(topdocs_src, output_path / "data" / "top_docs.json")

    # Copy images
    print("  Copying images...")

    # Document distribution
    doc_dist_src = source_path / f"{prefix}_document_dist.png"
    if doc_dist_src.exists():
        shutil.copy(doc_dist_src, output_path / "images" / "document_dist.png")

    # Temporal line
    temporal_line_src = source_path / f"{prefix}_temporal_topic_dist_quarter_line.png"
    if temporal_line_src.exists():
        shutil.copy(temporal_line_src, output_path / "images" / "temporal_line.png")

    # Temporal area
    temporal_area_src = source_path / f"{prefix}_temporal_topic_dist_quarter_stacked_area.png"
    if temporal_area_src.exists():
        shutil.copy(temporal_area_src, output_path / "images" / "temporal_area.png")

    # Yearly distribution
    yearly_src = source_path / f"{prefix}_topic_distribution_by_year.png"
    if yearly_src.exists():
        shutil.copy(yearly_src, output_path / "images" / "yearly_dist.png")

    # t-SNE visualization (try different naming patterns)
    tsne_patterns = [
        f"{prefix}_tsne_visualization.png",
        f"{prefix}_tsne.png",
        "tsne.png",
    ]
    tsne_copied = False
    for tsne_name in tsne_patterns:
        tsne_src = source_path / tsne_name
        if tsne_src.exists():
            shutil.copy(tsne_src, output_path / "images" / "tsne.png")
            tsne_copied = True
            break

    if not tsne_copied:
        print("  Note: t-SNE image not found in source folder")

    # UMAP visualization (try different naming patterns)
    umap_patterns = list(source_path.glob("*umap*visualization*.png")) + list(source_path.glob("*umap*.png"))
    has_umap = False
    if umap_patterns:
        shutil.copy(umap_patterns[0], output_path / "images" / "umap.png")
        has_umap = True
        print(f"  Copied UMAP visualization: {umap_patterns[0].name}")

    # Copy wordclouds
    wordclouds_src = source_path / "wordclouds"
    if wordclouds_src.exists():
        for wc in wordclouds_src.glob("Topic *.png"):
            shutil.copy(wc, output_path / "images" / "wordclouds" / wc.name)

    # Copy violin plot if exists (search for various naming patterns)
    has_violin_plot = False
    violin_patterns = list(source_path.glob("*violin*interactive*.html"))
    if violin_patterns:
        violin_src = violin_patterns[0]
        shutil.copy(violin_src, output_path / "violin-plot.html")
        has_violin_plot = True
        print(f"  Copied violin plot: {violin_src.name}")

    # Generate index.html
    print("  Generating index.html...")
    (output_path / "index.html").write_text(
        generate_index_html(method_upper, topic_count, dataset_title, has_violin_plot, has_umap)
    )

    # Generate topic-graph.html
    print("  Generating topic-graph.html...")
    csv_path = source_path / f"{prefix}_temporal_topic_dist_quarter.csv"
    if csv_path.exists():
        (output_path / "topic-graph.html").write_text(
            generate_topic_graph_html(csv_path, method_upper, topic_count)
        )
    else:
        print(f"  Warning: CSV file not found: {csv_path}")

    print(f"  Done creating {method_upper} app with {topic_count} topics!")

    return str(output_path)


def generate_all_apps(source_dir: str = "to_generate_from") -> list:
    """
    Generate apps for all valid folders in source_dir.

    Args:
        source_dir: Directory containing source folders

    Returns:
        List of paths to generated app directories
    """
    source_path = Path(source_dir)
    if not source_path.is_absolute():
        source_path = BASE_DIR / source_dir

    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")

    generated = []

    # Find all valid folders
    for folder in sorted(source_path.iterdir()):
        if not folder.is_dir():
            continue

        metadata = parse_folder_name(folder.name)
        if metadata:
            try:
                output = generate_app(str(folder))
                generated.append(output)
            except Exception as e:
                print(f"Error processing {folder.name}: {e}")

    return generated


def main():
    """Main entry point for CLI usage."""
    print("="*60)
    print("Dynamic Topic Analysis App Generator")
    print("="*60)

    generated = generate_all_apps()

    print("\n" + "="*60)
    print("Generation complete!")
    print("="*60)
    print("\nGenerated:")
    for path in generated:
        print(f"  - {path}")

    return 0


if __name__ == "__main__":
    exit(main())
