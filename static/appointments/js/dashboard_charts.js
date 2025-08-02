document.addEventListener("DOMContentLoaded", function () {
  const renderBarChart = (canvasId, data) => {
    if (!document.getElementById(canvasId)) return;

    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: Object.keys(data),
        datasets: [{
          label: canvasId.includes("checker") ? "Pallets" : "Loads",
          data: Object.values(data),
          backgroundColor: "#1F3BB3"
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: "#6B778C" },
            grid: { color: "#F0F0F0" }
          },
          x: {
            ticks: { color: "#6B778C" },
            grid: { display: false }
          }
        }
      }
    });
  };

  renderBarChart("checkerChartDay", checkerDayData);
  renderBarChart("checkerChartWeek", checkerWeekData);
  renderBarChart("checkerChartMonth", checkerMonthData);
  renderBarChart("statusChartDay", statusDayData);
  renderBarChart("statusChartWeek", statusWeekData);
  renderBarChart("statusChartMonth", statusMonthData);
});
