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
