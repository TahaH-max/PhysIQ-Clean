/**
 * Initialize the multi-step profile wizard.
 */
function initProfileWizard() {
  let currentStep = 1;
  const steps = document.querySelectorAll(".profile-step");

  /**
   * Show one profile step and hide the rest.
   * @param {number} step
   */
  function showStep(step) {
    steps.forEach(s => s.classList.add("d-none"));
    const target = document.querySelector(`.profile-step[data-step="${step}"]`);
    if (target) target.classList.remove("d-none");
    currentStep = step;
  }

  document.querySelectorAll(".profile-next").forEach(btn => {
    btn.addEventListener("click", () => showStep(currentStep + 1));
  });
  document.querySelectorAll(".profile-prev").forEach(btn => {
    btn.addEventListener("click", () => showStep(currentStep - 1));
  });

  const cards = document.querySelectorAll(".profile-goal");
  cards.forEach(card => {
    card.addEventListener("click", () => {
      const input = card.querySelector('input[type="radio"]');
      if (input) {
        input.checked = true;
        cards.forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");
      }
    });
  });

  const preChecked = document.querySelector('.profile-goal input[type="radio"]:checked');
  if (preChecked) {
    preChecked.closest('.profile-goal')?.classList.add('selected');
  }
}

/**
 * Initialize schedule grid selections for the profile form.
 */
function initScheduleGrid() {
  const grid = document.getElementById("schedule-grid");
  const scheduleInput = document.querySelector("input[name='schedule']");
  if (!grid || !scheduleInput) return;

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const hours = [8, 10, 12, 14, 16, 18]; // time blocks, every 2 hours
  const schedule = {};

  // Add top row of time labels.
  const topLabel = document.createElement("div");
  topLabel.classList.add("schedule-day");
  topLabel.textContent = ""; // blank top-left corner
  grid.appendChild(topLabel);

  hours.forEach(hour => {
    const timeLabel = document.createElement("div");
    timeLabel.classList.add("schedule-time");
    const ampm = hour < 12 ? "AM" : "PM";
    const displayHour = hour > 12 ? hour - 12 : hour;
    timeLabel.textContent = `${displayHour} ${ampm}`;
    grid.appendChild(timeLabel);
  });

  // Add day rows + clickable cells.
  days.forEach(day => {
    const dayLabel = document.createElement("div");
    dayLabel.classList.add("schedule-day");
    dayLabel.textContent = day;
    grid.appendChild(dayLabel);

    hours.forEach(hour => {
      const cell = document.createElement("div");
      cell.classList.add("schedule-slot");
      cell.dataset.day = day.toLowerCase();
      cell.dataset.hour = hour;
      cell.title = `${day} ${hour}:00 - ${hour + 2}:00`;

      cell.addEventListener("click", () => {
        cell.classList.toggle("busy");
        const d = cell.dataset.day;
        const h = `${hour}-${hour + 2}`;
        if (!schedule[d]) schedule[d] = [];
        if (cell.classList.contains("busy")) {
          schedule[d].push(h);
        } else {
          schedule[d] = schedule[d].filter(t => t !== h);
          if (schedule[d].length === 0) delete schedule[d];
        }
        scheduleInput.value = JSON.stringify(schedule);
      });

      grid.appendChild(cell);
    });
  });

  // Preload any existing data.
  try {
    const existing = JSON.parse(scheduleInput.value || "{}");
    for (const [day, blocks] of Object.entries(existing)) {
      // Normalize legacy day keys like "wed." -> "wednesday".
      let normalizedDay = day.replace(".", "").toLowerCase();
      if (normalizedDay === "wed") normalizedDay = "wednesday";
      blocks.forEach(h => {
        const start = h.split("-")[0];
        const cell = grid.querySelector(
          `.schedule-slot[data-day="${normalizedDay}"][data-hour="${start}"]`
        );
        if (cell) cell.classList.add("busy");
      });
    }
  } catch {}
}

document.addEventListener("DOMContentLoaded", () => {
  initProfileWizard();
  initScheduleGrid();
});

