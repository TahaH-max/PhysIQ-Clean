/* ---------------------------
   UPDATE STREAK DISPLAY
----------------------------*/
/**
 * Update streak counters in the UI.
 * @param {{workout_current:number, workout_best:number, nutrition_current:number, nutrition_best:number, overall_current:number, overall_best:number}} streaks
 */
function updateStreakDisplay(streaks) {
    const cards = document.querySelectorAll('.progress-streak-card');
    if (cards.length < 3) return;

    const sets = [
        { current: streaks.workout_current, best: streaks.workout_best },
        { current: streaks.nutrition_current, best: streaks.nutrition_best },
        { current: streaks.overall_current, best: streaks.overall_best }
    ];

    sets.forEach((st, i) => {
        const card = cards[i];

        const val = card.querySelector(".progress-streak-value");
        val.innerHTML = "";
        const label = st.current === 1 ? "day" : "days";
        val.append(
            document.createTextNode(st.current + " "),
            (() => {
                const s = document.createElement("span");
                s.className = "streak-unit";
                s.textContent = label;
                return s;
            })()
        );

        card.querySelector(".progress-streak-best").textContent = "Best: " + st.best;
    });
}

/* ---------------------------
   UI ELEMENT UPDATES
----------------------------*/
/**
 * Update a day indicator UI element after a save.
 * @param {string} dateStr
 * @param {"workout"|"nutrition"} type
 * @param {string} status
 */
function updateIndicator(dateStr, type, status) {
    const col = document.querySelector(`.progress-day[data-date="${dateStr}"]`);
    if (!col) return;

    const indicator = col.querySelector(`.progress-${type}`);
    indicator.dataset.status = status;

    const icon = indicator.querySelector(".progress-status-icon");

    // Remove all icon classes first
    icon.className = "progress-status-icon bi";

    // Apply new icon based on type and status
    if (type === "workout") {
        switch (status) {
            case "done":
                icon.classList.add("bi-check-circle-fill", "text-success");
                break;
            case "rest":
                icon.classList.add("bi-circle", "text-secondary");
                break;
            case "missed":
            default:
                icon.classList.add("bi-x-circle-fill", "text-danger");
                break;
        }
    } else if (type === "nutrition") {
        switch (status) {
            case "hit":
                icon.classList.add("bi-droplet-fill", "text-success");
                break;
            case "none":
                icon.classList.add("bi-circle", "text-secondary");
                break;
            case "missed":
            default:
                icon.classList.add("bi-droplet-half", "text-danger");
                break;
        }
    }

    // Subtle feedback pulse
    icon.classList.add("pulse");
    setTimeout(() => icon.classList.remove("pulse"), 300);
}

/* ---------------------------
   API CALLS
----------------------------*/
/**
 * Persist workout/nutrition status for a day.
 * @param {string} dateStr
 * @param {string|null} workoutStatus
 * @param {string|null} nutritionStatus
 */
function saveProgress(dateStr, workoutStatus, nutritionStatus) {
    postJson('/api/progress/update/', {
        date: dateStr,
        workout_status: workoutStatus,
        nutrition_status: nutritionStatus,
    }).then(data => {
        if (!data.success) return;

        updateIndicator(dateStr, "workout", data.workout_status);
        updateIndicator(dateStr, "nutrition", data.nutrition_status);
        updateStreakDisplay(data.streaks);
    });
}

/**
 * Persist notes for a day.
 * @param {string} dateStr
 * @param {string} notes
 */
function saveNote(dateStr, notes) {
    postJson('/api/progress/note/', { date: dateStr, notes }).then(data => {
        if (!data.success) return;
        updateNoteButton(dateStr, data.notes);
    });
}

/**
 * Update the notes button state for a specific day.
 * @param {string} dateStr
 * @param {string} notes
 */
function updateNoteButton(dateStr, notes) {
    const btn = document.querySelector(`.progress-note[data-date="${dateStr}"]`);
    if (!btn) return;

    const hasNotes = Boolean(notes && notes.trim());
    btn.dataset.notes = notes || "";
    btn.classList.toggle("has-notes", hasNotes);

    const icon = btn.querySelector("i");
    if (icon) {
        icon.classList.toggle("bi-pencil-fill", hasNotes);
        icon.classList.toggle("bi-pencil-square", !hasNotes);
    }
}

/* ---------------------------
   INITIALIZATION
----------------------------*/
/**
 * Initialize progress tab interactions.
 */
function initProgress() {

    /* Workout click cycle */
    document.querySelectorAll(".progress-workout").forEach(ind => {
        ind.onclick = function () {
            const col = this.closest(".progress-day");
            const dateStr = col.dataset.date;

            const cycle = { "done": "rest", "rest": "missed", "missed": "done" };
            const newStatus = cycle[this.dataset.status];

            const nutrition = col.querySelector(".progress-nutrition").dataset.status;

            saveProgress(dateStr, newStatus, nutrition);
        };
    });

    /* Nutrition click cycle */
    document.querySelectorAll(".progress-nutrition").forEach(ind => {
        ind.onclick = function () {
            const col = this.closest(".progress-day");
            const dateStr = col.dataset.date;

            const cycle = { "hit": "none", "none": "missed", "missed": "hit" };
            const newStatus = cycle[this.dataset.status];

            const workout = col.querySelector(".progress-workout").dataset.status;

            saveProgress(dateStr, workout, newStatus);
        };
    });

    /* Notes modal */
    document.querySelectorAll(".progress-note").forEach(btn => {
        btn.onclick = function () {
            const dateStr = this.dataset.date;
            const notes = this.dataset.notes;
            const col = this.closest(".progress-day");

            document.getElementById("edit-date").value = dateStr;
            document.getElementById("day-notes").value = notes;

            /* Safe radio selection */
            const workout = col.querySelector(".progress-workout").dataset.status;
            const nutrition = col.querySelector(".progress-nutrition").dataset.status;

            const wr = document.getElementById(`workout-${workout}`);
            const nr = document.getElementById(`nutrition-${nutrition}`);

            if (wr) wr.checked = true;
            if (nr) nr.checked = true;

            /* Modal */
            const modalEl = document.getElementById("editDayModal");
            const modal = new bootstrap.Modal(modalEl, { backdrop: true });
            modal.show();
        };
    });

    /* Save modal */
    document.getElementById("save-day-btn").onclick = function () {
        const dateStr = document.getElementById("edit-date").value;
        const notes = document.getElementById("day-notes").value;

        const workout = document.querySelector("input[name='workout-status']:checked")?.value || "missed";
        const nutrition = document.querySelector("input[name='nutrition-status']:checked")?.value || "none";

        saveProgress(dateStr, workout, nutrition);
        saveNote(dateStr, notes);

        bootstrap.Modal.getInstance(document.getElementById("editDayModal")).hide();
    };
}

/* Auto init */
document.addEventListener("DOMContentLoaded", initProgress);

