document.addEventListener('DOMContentLoaded', () => {
    const views = {
        settings: document.getElementById('settings-view'),
        main: document.getElementById('main-view')
    };

    // Load saved data
    chrome.storage.local.get(['apiKey', 'resumeText'], (data) => {
        if (data.apiKey) document.getElementById('api-key').value = data.apiKey;
        if (data.resumeText) document.getElementById('resume-text').value = data.resumeText;

        // If no key, show settings immediately
        if (!data.apiKey) toggleSettings(true);
    });

    // Buttons
    document.getElementById('open-settings').onclick = () => toggleSettings(true);
    document.getElementById('save-settings').onclick = saveSettings;
    document.getElementById('scan-btn').onclick = scanJob;

    function toggleSettings(show) {
        if (show) {
            views.settings.classList.remove('hidden');
            views.main.classList.add('hidden');
        } else {
            views.settings.classList.add('hidden');
            views.main.classList.remove('hidden');
        }
    }

    function saveSettings() {
        const apiKey = document.getElementById('api-key').value;
        const resume = document.getElementById('resume-text').value;
        chrome.storage.local.set({ apiKey, resumeText: resume }, () => {
            toggleSettings(false);
        });
    }

    async function scanJob() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('results').classList.add('hidden');
        document.getElementById('score-box').classList.add('hidden');

        // 1. Scrape the active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => document.body.innerText
        }, async (results) => {
            if (!results || !results[0]) return;

            const jobText = results[0].result.substring(0, 5000); // Limit length
            analyzeWithGemini(jobText);
        });
    }

    async function analyzeWithGemini(jobText) {
        chrome.storage.local.get(['apiKey', 'resumeText'], async (data) => {
            if (!data.apiKey || !data.resumeText) {
                alert("Please set your API Key and Resume in Settings first!");
                return;
            }

            const prompt = `
        Compare this Resume to the Job Description.
        
        RESUME: ${data.resumeText.substring(0, 3000)}
        
        JOB: ${jobText}
        
        Output strictly in JSON format:
        {
          "score": (number 0-100),
          "missing_keywords": ["keyword1", "keyword2", "keyword3"],
          "verdict": "Short sentence summary"
        }
      `;

            try {
                const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${data.apiKey}`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{ parts: [{ text: prompt }] }]
                    })
                });

                const json = await response.json();
                const rawText = json.candidates[0].content.parts[0].text;

                // Clean up markdown json block if present
                const cleanJson = rawText.replace(/```json/g, '').replace(/```/g, '').trim();
                const result = JSON.parse(cleanJson);

                displayResults(result);

            } catch (error) {
                alert("AI Error: " + error.message);
                document.getElementById('loading').classList.add('hidden');
            }
        });
    }

    function displayResults(data) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('score-box').classList.remove('hidden');
        document.getElementById('results').classList.remove('hidden');

        document.getElementById('match-score').innerText = data.score;
        document.getElementById('match-verdict').innerText = data.verdict;

        // Color code
        const circle = document.querySelector('.score-circle');
        if (data.score > 80) circle.style.borderColor = "#4CAF50"; // Green
        else if (data.score > 50) circle.style.borderColor = "#FFC107"; // Yellow
        else circle.style.borderColor = "#F44336"; // Red

        // List keywords
        const list = document.getElementById('missing-list');
        list.innerHTML = '';
        data.missing_keywords.forEach(kw => {
            const li = document.createElement('li');
            li.innerText = kw;
            list.appendChild(li);
        });
    }
});
