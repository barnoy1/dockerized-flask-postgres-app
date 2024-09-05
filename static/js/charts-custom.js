document.addEventListener("DOMContentLoaded", function () {
    Chart.defaults.color = "#75787c";

    const LINECHARTEXMPLE = document.getElementById("lineChartCustom1"),
          SCATTERCHART = document.getElementById("scatterChartCustom1"),
          SCATTERCHART2 = document.getElementById("scatterChartCustom2"),
          PIECHARTEXMPLE = document.getElementById("pieChartCustom1"),
          PIECHART = document.getElementById("doughnutChartCustom1");
  
    // ------------------------------------------------------- //
    // Scatter Chart Custom 1
    // ------------------------------------------------------ //
    var scatterChartExample = new Chart(SCATTERCHART, {
        type: "line",
        options: {
            plugins: {
                legend: { 
                    labels: { 
                        color: "#777",
                        font: {
                            size: 12
                        } 
                    }
                },
                tooltip: { // Use tooltip instead of tooltips
                    callbacks: {
                        label: function(tooltipItem) {
                            const label = tooltipItem.dataset.label;
                            const value = tooltipItem.raw.y;
                            const date = tooltipItem.label;
                            const remarks = [
                                'No remark',  // For January 2nd
                                'No remark',  // For January 3rd
                                'Sales spike due to promotion.',  // For January 4th
                                'No remark',  // For January 5th
                                'No remark',  // For January 6th
                                'Inventory low.'  // For January 7th
                            ];
                            const remark = remarks[tooltipItem.dataIndex];
                            return `${label}: ${value} on ${date} ${remark}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Sales'
                    }
                }
            }
        },
        data: {
            labels: [
                '2024-01-02', '2024-01-03', '2024-01-04', 
                '2024-01-05', '2024-01-06', '2024-01-07'
            ].map(date => luxon.DateTime.fromISO(date).toFormat('dd MMM yyyy')),
            datasets: [{
                label: 'Sales',
                data: [24, 52, 10, 81, 56, 55],
                fill: false,
                tension: 0,
                backgroundColor: "rgba(134, 77, 217, 0.88)",
                borderColor: "rgba(134, 77, 217, 0.88)",
                borderWidth: 1,
                pointBorderColor: "rgba(134, 77, 217, 0.88)",
                pointBackgroundColor: "#fff",
                pointBorderWidth: 1,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(134, 77, 217, 0.88)",
                pointHoverBorderColor: "rgba(134, 77, 217, 0.88)",
                pointHoverBorderWidth: 2,
                pointRadius: 3,
                pointHitRadius: 10,
                spanGaps: false
            }]
        }
    });

    // ------------------------------------------------------- //
    // Scatter Chart Custom 2
    // ------------------------------------------------------ //
    var scatterChartExample = new Chart(SCATTERCHART2, {
        type: 'scatter',
        options: {
            scales: {
                x: {
                    type: 'time', // Use time scale for x-axis
                    time: {
                        unit: 'day', // Define the time unit
                        displayFormats: {
                            day: 'dd LLL yyyy' // Format the date
                        },
                        tooltipFormat: 'dd LLL yyyy' // Format the tooltip date
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    ticks: {
                        autoSkip: true,
                        maxRotation: 60,
                        minRotation: 60
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Values'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += `(${context.raw.x}, ${context.raw.y})`;
                            if (context.raw.comment) {
                                label += ` - ${context.raw.comment}`;
                            }
                            return label;
                        }
                    }
                }
            }
        },
        data: {
            datasets: [
                {
                    label: 'Dataset 1',
                    data: [
                        {x: '2024-07-01T10:00:00', y: 10, comment: 'Comment for entry 1'},
                        {x: '2024-07-02T11:00:00', y: 15, comment: 'Comment for entry 2'},
                        {x: '2024-07-03T12:00:00', y: 7, comment: 'Comment for entry 3'},
                        {x: '2024-07-04T13:00:00', y: 20, comment: 'Comment for entry 4'}
                    ],
                    backgroundColor: 'rgba(255, 99, 132, 1)',
                    pointStyle: 'triangle', // Custom marker shape
                    pointRadius: 10
                },
                {
                    label: 'Dataset 2',
                    data: [
                        {x: '2024-07-02T11:00:00', y: 10, comment: 'Comment for entry 5'},
                        {x: '2024-07-03T12:00:00', y: 15, comment: 'Comment for entry 6'},
                        {x: '2024-07-05T14:00:00', y: 7, comment: 'Comment for entry 7'},
                        {x: '2024-07-06T15:00:00', y: 12, comment: 'Comment for entry 8'}
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 1)',
                    pointStyle: 'rect', // Custom marker shape
                    pointRadius: 10
                },
                {
                    label: 'Dataset 3',
                    data: [
                        {x: '2024-07-01T10:00:00', y: 5, comment: 'Comment for entry 9'},
                        {x: '2024-07-04T13:00:00', y: 8, comment: 'Comment for entry 10'},
                        {x: '2024-07-05T14:00:00', y: 10, comment: 'Comment for entry 11'},
                        {x: '2024-07-07T16:00:00', y: 15, comment: 'Comment for entry 12'}
                    ],
                    backgroundColor: 'rgba(75, 192, 192, 1)',
                    pointStyle: 'circle', // Custom marker shape
                    pointRadius: 10
                }
            ]
        }
    });

    // ------------------------------------------------------- //
    // Pie Chart Custom 1
    // ------------------------------------------------------ //
    // Chart.register(ChartDataLabels);
    var pieChartExample = new Chart(PIECHARTEXMPLE, {
        type: "pie",
        options: {
            plugins: {
                datalabels: {
                    formatter: (value, ctx) => {
                        let sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        let percentage = (value * 100 / sum).toFixed(2) + "%";
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold',
                        size: 16
                    }
                },
                legend: {
                    display: true,
                    position: "right",
                    align: "center",
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 25
                    }
                },
            }
        },
        data: {
            labels: ["A", "B", "C", "D"],
            datasets: [{
                data: [300, 50, 100, 80],
                borderWidth: 0,
                backgroundColor: ["#723ac3", "#864DD9", "#9762e6", "#a678eb"],
                hoverBackgroundColor: ["#723ac3", "#864DD9", "#9762e6", "#a678eb"]
            }]
        },
        plugins: [ChartDataLabels]
    });

    // ------------------------------------------------------- //
    // Doughnut Chart Custom
    // ------------------------------------------------------ //
    var myPieChart = new Chart(PIECHART, {
        type: "doughnut",
        options: {
            cutout: '30%',
            plugins: {
                legend: {
                    display: true,
                    position: "right",
                    align: "center",
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 25
                    }
                },
                datalabels: {
                    formatter: (value, ctx) => {
                        let sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        let percentage = (value * 100 / sum).toFixed(2) + "%";
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold',
                        size: 16
                    }
                }
            }
        },
        data: {
            labels: ["A", "B", "C", "D"],
            datasets: [{
                data: [120, 90, 77, 95],
                borderWidth: [0, 0, 0, 0],
                backgroundColor: ["#b53dde", "#CF53F9", "#d06cf2", "#de97f6"],
                hoverBackgroundColor: ["#b53dde", "#CF53F9", "#d06cf2", "#de97f6"]
            }]
        },
        plugins: [ChartDataLabels]
    });    
});
