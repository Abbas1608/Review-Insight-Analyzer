document.getElementById("analyze-btn").addEventListener("click", function () {
    const urlInput = document.getElementById("product-url").value;
    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("results-section");
    const errorMessage = document.getElementById("error-message");

    resultSection.classList.add("hidden");
    errorMessage.classList.add("hidden");
    loading.classList.remove("hidden");

    fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput })
    })
        .then(response => response.json())
        .then(data => {
            loading.classList.add("hidden");
            if (data.success) {
                document.getElementById("positive-percentage").textContent = `${data.sentiment.positive}%`;
                document.getElementById("negative-percentage").textContent = `${data.sentiment.negative}%`;
                document.getElementById("neutral-percentage").textContent = `${data.sentiment.neutral}%`;
                document.getElementById("total-reviews").textContent = data.total_reviews;
                resultSection.classList.remove("hidden");
            } else {
                errorMessage.classList.remove("hidden");
            }
        })
        .catch(error => {
            loading.classList.add("hidden");
            errorMessage.classList.remove("hidden");
        });
});
