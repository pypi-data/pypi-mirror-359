import React, { useEffect, useRef } from 'react';

/**
 * PieChart - Chart.js wrapper for pie charts
 * 
 * @param {Object} props
 * @param {Array<string>} props.labels - Labels for each segment
 * @param {Array<number>} props.data - Data values for each segment
 * @param {Array<string>} props.colors - Colors for each segment (defaults to blue palette)
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels
 * @param {boolean} props.showLegend - Whether to show legend
 * @param {string} props.legendPosition - Legend position: "top", "bottom", "left", "right"
 * @param {boolean} props.showDataLabels - Whether to show data labels on segments
 */
export const PieChart = ({ 
  labels = [],
  data = [],
  colors = ['#1D4ED8', '#3B82F6', '#93C5FD', '#DBEAFE', '#EBF5FF'],
  title,
  height = 240,
  showLegend = true,
  legendPosition = 'bottom',
  showDataLabels = false,
  className = ''
}) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Destroy existing chart if it exists
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // Create new chart
    const ctx = canvasRef.current.getContext('2d');
    
    // Dynamically import Chart.js
    import('chart.js/auto').then((ChartModule) => {
      const Chart = ChartModule.default;
      
      chartRef.current = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, data.length),
            borderWidth: 0,
            hoverBorderWidth: 2,
            hoverBorderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: showLegend,
              position: legendPosition,
              labels: {
                padding: 20,
                font: {
                  size: 14,
                  family: "'Montserrat', sans-serif"
                },
                usePointStyle: true,
                pointStyle: 'circle'
              }
            },
            title: {
              display: !!title,
              text: title,
              font: {
                size: 18,
                family: "'Montserrat', sans-serif",
                weight: '600'
              },
              padding: {
                bottom: 20
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleFont: {
                family: "'Montserrat', sans-serif",
                size: 14
              },
              bodyFont: {
                family: "'Montserrat', sans-serif",
                size: 13
              },
              padding: 12,
              cornerRadius: 8,
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            },
            datalabels: showDataLabels ? {
              display: true,
              color: '#ffffff',
              font: {
                family: "'Montserrat', sans-serif",
                size: 16,
                weight: 'bold'
              },
              formatter: (value, context) => {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(0);
                return percentage + '%';
              }
            } : {
              display: false
            }
          },
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1000
          }
        }
      });
    });

    // Cleanup function
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [labels, data, colors, title, height, showLegend, legendPosition, showDataLabels]);

  return (
    <div className={`bg-white ${className}`}>
      <div style={{ height: `${height}px` }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
};

export default PieChart;