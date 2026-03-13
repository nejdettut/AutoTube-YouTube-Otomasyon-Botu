const API_BASE_URL = "http://localhost:8000"; // Canlı ortamda bu Vercel'den Render linkine değiştirilecek

let pollInterval;

async function startGeneration() {
    const topic = document.getElementById("topicInput").value.trim();
    const btn = document.getElementById("generateBtn");

    // UI Güncelleme
    btn.disabled = true;
    btn.innerHTML = `<span>Başlıyor...</span>`;
    document.getElementById("resultSection").classList.add("hidden");

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ topic: topic })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("statusSection").classList.remove("hidden");
            document.getElementById("statusTitle").innerText = "Video Üretiliyor...";
            pollStatus(data.job_id);
        } else {
            alert("Hata: " + (data.detail || "Bilinmeyen hata"));
            resetBtn();
        }

    } catch (err) {
        alert("Sunucuya bağlanılamadı. API açık mı?");
        console.error(err);
        resetBtn();
    }
}

function pollStatus(jobId) {
    let progress = 0;

    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
            const data = await res.json();

            // Adımları Güncelle
            renderSteps(data.log?.steps || {});

            // Durumu kontrol et
            if (data.status === "completed") {
                clearInterval(pollInterval);
                document.getElementById("progressFill").style.width = "100%";
                document.getElementById("statusTitle").innerText = "Video Başarıyla Üretildi!";
                showResult(data);
                resetBtn();
            } else if (data.status === "error") {
                clearInterval(pollInterval);
                document.getElementById("progressFill").style.background = "#ef4444";
                document.getElementById("statusTitle").innerText = "Hata Oluştu!";
                alert("Hata: " + data.error);
                resetBtn();
            } else {
                // Yapılan adım sayısına göre sahte bir ilerleme barı doldur
                const stepCount = Object.keys(data.log?.steps || {}).length;
                progress = Math.min((stepCount / 6) * 100, 95);
                document.getElementById("progressFill").style.width = `${progress}%`;
            }
        } catch (err) {
            console.error("Durum çekilemedi", err);
        }
    }, 2000);
}

function renderSteps(stepsObj) {
    const stepsList = document.getElementById("stepsList");
    stepsList.innerHTML = "";

    const stepNames = {
        content: "Senaryo & İçerik",
        audio: "Seslendirme (Edge-TTS)",
        subtitle: "Altyazılar",
        images: "Görseller & Medya",
        video: "Video Montajı",
        upload: "YouTube'a Yükleme"
    };

    for (const [key, name] of Object.entries(stepNames)) {
        const li = document.createElement("li");

        let statusText = "Bekliyor...";
        if (stepsObj[key]) {
            statusText = stepsObj[key];
            if (!statusText.includes("✓") && !statusText.includes("✗")) {
                li.classList.add("step-active");
            }
        }

        li.innerHTML = `<span>${name}</span> <span>${statusText}</span>`;
        stepsList.appendChild(li);
    }
}

function showResult(data) {
    const resultSection = document.getElementById("resultSection");
    resultSection.classList.remove("hidden");

    // Video URL (Backend'den statik olarak sunulmalı)
    if (data.video_url) {
        const videoEl = document.getElementById("resultVideo");
        videoEl.src = `${API_BASE_URL}${data.video_url}`;
    }

    // Meta Data
    if (data.content) {
        document.getElementById("resTitle").innerText = data.content.title || "-";
        document.getElementById("resDescription").innerText = data.content.description || "-";

        // Tags
        const tagsContainer = document.getElementById("resTags");
        tagsContainer.innerHTML = "";
        (data.content.tags || []).forEach(tag => {
            const span = document.createElement("span");
            span.className = "tag";
            span.innerText = `#${tag}`;
            tagsContainer.appendChild(span);
        });
    }

    // YouTube Linki
    if (data.youtube_url) {
        const ytBtn = document.getElementById("youtubeLink");
        ytBtn.href = data.youtube_url;
        ytBtn.classList.remove("hidden");
    }
}

function resetBtn() {
    const btn = document.getElementById("generateBtn");
    btn.disabled = false;
    btn.innerHTML = `<span>Videoyu Üret</span>
    <svg viewBox="0 0 24 24" fill="none" class="rocket-icon"><path d="M12 2.5L9.5 8H14.5L12 2.5Z" fill="currentColor"/><path d="M5 19L7 14L12 17L5 19Z" fill="currentColor"/><path d="M19 19L17 14L12 17L19 19Z" fill="currentColor"/><path d="M12 17L7 14V8H17V14L12 17Z" fill="currentColor"/></svg>`;
}
