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
    return text.replace(/\s+/g, ' ').trim().split(' ').slice(0, 100).join(' ');
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
