/** Dashboard content container. */
const contentArea = document.getElementById('content-area');
/** Sidebar navigation links for views. */
const sidebarLinks = document.querySelectorAll('#sidebar a');
/** Loading overlay shown during view swaps. */
const loader = document.getElementById('loader-overlay');

/** Map of dashboard routes to init functions. */
const viewRegistry = {
    "/overview": {
        init: () => initOverview?.(),
    },
    "/workout": {
        init: () => {
            workoutModifyHandler();
            initWorkout?.();
        },
    },
    "/nutrition": {
        init: () => initNutrition?.(),
    },
    "/chat": {
        init: () => {
            initChat?.();
            initPromptBubbles?.();
        },
    },
    "/progress": {
        init: () => initProgress?.(),
    },
    "/photo-locker": {
        init: () => initPhotoPreview?.(),
    },
    "/community-feed": {
        init: () => initPhotoPreview?.(),
    },
};

/** Track prefetched CSS to avoid duplicate preload links. */
const prefetchedCss = new Set();

/**
 * Parse a comma-separated CSS path list into trimmed entries.
 * @param {string} value
 * @returns {string[]}
 */
function parseCssList(value) {
    return (value || '')
        .split(/\s+/)
        .map(s => s.trim())
        .filter(Boolean);
}

/**
 * Read CSS hints from a partial's data-css attribute.
 * @param {HTMLElement} root
 * @returns {string[]}
 */
function getViewCssList(root) {
    const view = root.querySelector('.dashboard-view');
    if (!view) return [];
    return parseCssList(view.dataset.css);
}

/**
 * Preload stylesheets to reduce view switch latency.
 * @param {string[]} cssList
 */
function prefetchCssList(cssList) {
    cssList.forEach(href => {
        if (!href || prefetchedCss.has(href)) return;
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = href;
        link.dataset.prefetchCss = href;
        link.onload = () => {
            prefetchedCss.add(href);
        };
        link.onerror = () => {
            link.remove();
        };
        document.head.appendChild(link);
    });
}

/**
 * Swap in the CSS list for the current dashboard view.
 * @param {string[]} cssList
 */
function applyPartialCss(cssList) {
    const existingLinks = Array.from(document.querySelectorAll('link[data-dynamic-css]'));
    const existingMap = new Map(existingLinks.map(link => [link.dataset.dynamicCss, link]));

    // Remove old styles not needed for the current view
    existingMap.forEach((link, href) => {
        if (!cssList.includes(href)) {
            link.remove();
            existingMap.delete(href);
        }
    });

    const loadPromises = [];
    // Add missing styles for the current view
    cssList.forEach(href => {
        if (existingMap.has(href)) return;
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.dataset.dynamicCss = href;
        document.head.appendChild(link);

        loadPromises.push(new Promise(resolve => {
            link.onload = () => resolve();
            link.onerror = () => resolve();
        }));
    });

    return Promise.all(loadPromises);
}

/**
 * Display the loading overlay with a custom message.
 * @param {string} [message]
 */
function showLoader(message = "Your coach AI is preparing your plan...") {
    loader.querySelector("p").textContent = message;
    loader.classList.remove("d-none");
    requestAnimationFrame(() => loader.style.opacity = "1");
}

/** Hide the dashboard loading overlay. */
function hideLoader() {
    loader.style.opacity = "0";
    setTimeout(() => loader.classList.add("d-none"), 400);
}

sidebarLinks.forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();

        const clickedLink = e.currentTarget;
        const viewName = clickedLink.getAttribute('data-view');
        const hintedCss = parseCssList(clickedLink.dataset.css);
        prefetchCssList(hintedCss);

        sidebarLinks.forEach(l => l.classList.remove('active'));
        clickedLink.classList.add('active');

        // Hide content immediately to avoid flicker while the loader animates.
        contentArea.classList.add("d-none");
        showLoader("Loading your dashboard...");

        fetchHtml(`/dashboard${viewName}`)
            .then(data => {
                contentArea.innerHTML = data;
                const cssList = getViewCssList(contentArea);
                return applyPartialCss(cssList).then(() => cssList);
            })
            .then(() => {
                viewRegistry[viewName]?.init?.();
            })
            .catch(error => {
                contentArea.innerHTML = `
                    <div class="alert alert-danger text-center mt-5">
                        Failed to load this section. Please try again later.
                    </div>`;
                console.error(error);
            })
            .finally(() => {
                hideLoader();
                // Show content only after loader fade-out.
                contentArea.classList.remove("d-none");
            });
    });
});

/** Bind workout regeneration modal handlers. */
function workoutModifyHandler() {
  const submitBtn = document.querySelector("#submit-modify-plan");
  if (!submitBtn) return;

  submitBtn.onclick = async () => {
    const payload = {
      goal: document.getElementById("goal-input").value.trim(),
      schedule: document.getElementById("schedule-input").value.trim(),
      notes: document.getElementById("notes-input").value.trim(),
    };

    bootstrap.Modal.getInstance(document.querySelector("#modifyPlanModal")).hide();

    // Optional loader if you're using one
    showLoader?.("Updating workout plan...");

    const html = await postHtml("/dashboard/workout/", payload);
    document.getElementById("content-area").innerHTML = html;

    // Re-bind button to new DOM
    workoutModifyHandler();

    hideLoader?.();
  };
}

/**
 * Change the current dashboard view by name.
 * @param {string} viewName
 */
function goToTab(viewName) {
    // Normalize (allow "workout" or "/workout")
    const target = viewName.startsWith("/") ? viewName : `/${viewName}`;

    const link = document.querySelector(`#sidebar a[data-view="${target}"]`);
    if (link) link.click();
}


document.addEventListener("DOMContentLoaded", () => {
    const initialCss = getViewCssList(document);
    if (initialCss.length) {
        applyPartialCss(initialCss);
    }

    sidebarLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            prefetchCssList(parseCssList(link.dataset.css));
        });
    });

    const params = new URLSearchParams(window.location.search);
    const tab = params.get("tab");

    if (tab) {
        goToTab(tab);
        history.replaceState(null, "", "/dashboard/");
    } else {
        goToTab("overview");
    }
});

