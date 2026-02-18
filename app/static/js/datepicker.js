document.addEventListener("DOMContentLoaded", () => {
  const dateInputs = document.querySelectorAll("[data-datepicker]");

  if (!dateInputs.length) return;

  dateInputs.forEach(input => {
    const picker = new Datepicker(input, {
      autohide: true,
      format: "yyyy-mm-dd",
      todayHighlight: true
    });

    // Optional: auto-submit via query string - need to review how this works before using
    if (input.dataset.reload === "true") {
      input.addEventListener("changeDate", () => {
        const url = new URL(window.location.href);
        url.searchParams.set(input.name || "date", input.value);
        window.location.href = url.toString();
      });
    }
  });
});
