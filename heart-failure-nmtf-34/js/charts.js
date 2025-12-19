/**
 * Chart.js Configurations and Visualizations
 */

const Charts = {
    coherenceChart: null,

    // Color palette for topics
    colors: [
        '#2563eb', '#7c3aed', '#db2777', '#dc2626', '#ea580c',
        '#d97706', '#ca8a04', '#65a30d', '#16a34a', '#059669',
        '#0d9488', '#0891b2', '#0284c7', '#2563eb', '#4f46e5',
        '#7c3aed', '#9333ea', '#c026d3', '#db2777', '#e11d48',
        '#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'
    ],

    /**
     * Initialize all charts
     */
    init() {
        this.initCoherenceChart();
    },

    /**
     * Initialize the coherence scores bar chart
     */
    initCoherenceChart() {
        const ctx = document.getElementById('coherence-chart');
        if (!ctx) return;

        const scores = TopicData.getCoherenceScores();

        const data = {
            labels: scores.map(s => `Topic ${s.topicNum}`),
            datasets: [{
                label: 'Coherence Score (C_V)',
                data: scores.map(s => s.score),
                backgroundColor: scores.map((_, i) => this.colors[i % this.colors.length]),
                borderColor: scores.map((_, i) => this.colors[i % this.colors.length]),
                borderWidth: 1,
                borderRadius: 4,
                barThickness: 20
            }]
        };

        const averageCoherence = TopicData.getAverageCoherence();

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Coherence: ${context.raw.toFixed(4)}`;
                            },
                            afterLabel: function(context) {
                                const topicNum = context.dataIndex + 1;
                                const topWords = TopicData.getTopWords(topicNum, 3);
                                return `Top words: ${topWords.map(w => w.word).join(', ')}`;
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            averageLine: {
                                type: 'line',
                                yMin: averageCoherence,
                                yMax: averageCoherence,
                                borderColor: '#dc2626',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    display: true,
                                    content: `Avg: ${averageCoherence.toFixed(3)}`,
                                    position: 'end'
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: false,
                        min: 0.4,
                        max: 1.0,
                        grid: {
                            color: '#e2e8f0'
                        },
                        title: {
                            display: true,
                            text: 'Coherence Score (C_V)'
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const topicNum = index + 1;
                        showTopicModal(topicNum);
                    }
                }
            }
        };

        this.coherenceChart = new Chart(ctx, config);
    },

    /**
     * Get color for a specific topic
     */
    getTopicColor(topicNum) {
        return this.colors[(topicNum - 1) % this.colors.length];
    },

    /**
     * Destroy all charts (for cleanup)
     */
    destroy() {
        if (this.coherenceChart) {
            this.coherenceChart.destroy();
            this.coherenceChart = null;
        }
    }
};

// Export for use in other modules
window.Charts = Charts;
