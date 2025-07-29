import React, { useEffect, useRef } from 'react';

/**
 * BarChart - Chart.js wrapper for bar charts
 * 
 * @param {Object} props
 * @param {Array<string>} props.labels - Labels for each bar
 * @param {Array<Object>} props.datasets - Array of dataset objects with label, data, and optional backgroundColor
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels
 * @param {boolean} props.horizontal - Whether to display horizontal bars
 * @param {boolean} props.stacked - Whether to stack bars
 * @param {boolean} props.showLegend - Whether to show legend
 * @param {Object} props.scales - Custom scale configuration
 * @param {string} props.xAxisLabel - Label for X axis
 * @param {string} props.yAxisLabel - Label for Y axis
 */
export const BarChart = ({ 
  labels = [],
  datasets = [],
  title,
  height = 300,
  horizontal = false,
  stacked = false,
  showLegend = true,
  scales,
  xAxisLabel,
  yAxisLabel,
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
      
      // Default colors for datasets
      const defaultColors = ['#1D4ED8', '#3B82F6', '#93C5FD', '#10B981', '#F59E0B'];
      
      // Process datasets
      const processedDatasets = datasets.map((dataset, index) => ({
        label: dataset.label || `Dataset ${index + 1}`,
        data: dataset.data || [],
        backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
        borderColor: dataset.borderColor || 'transparent',
        borderWidth: dataset.borderWidth || 0,
        borderRadius: dataset.borderRadius || 4,
        hoverBackgroundColor: dataset.hoverBackgroundColor || dataset.backgroundColor || defaultColors[index % defaultColors.length],
        barThickness: dataset.barThickness || undefined,
        maxBarThickness: dataset.maxBarThickness || 50
      }));

      const defaultScales = {
        x: {
          stacked: stacked,
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            font: {
              family: "'Montserrat', sans-serif",
              size: 12
            },
            color: '#6B7280'
          },
          title: {
            display: !!xAxisLabel,
            text: xAxisLabel,
            font: {
              family: "'Montserrat', sans-serif",
              size: 14,
              weight: '600'
            },
            color: '#374151'
          }
        },
        y: {
          stacked: stacked,
          beginAtZero: true,
          grid: {
            color: '#E5E7EB',
            drawBorder: false
          },
          ticks: {
            font: {
              family: "'Montserrat', sans-serif",
              size: 12
            },
            color: '#6B7280',
            callback: function(value) {
              // Format large numbers
              if (value >= 1000000) {
                return '€' + (value / 1000000).toFixed(1) + 'M';
              } else if (value >= 1000) {
                return '€' + (value / 1000).toFixed(0) + 'K';
              }
              return '€' + value;
            }
          },
          title: {
            display: !!yAxisLabel,
            text: yAxisLabel,
            font: {
              family: "'Montserrat', sans-serif",
              size: 14,
              weight: '600'
            },
            color: '#374151'
          }
        }
      };

      chartRef.current = new Chart(ctx, {
        type: horizontal ? 'bar' : 'bar',
        data: {
          labels: labels,
          datasets: processedDatasets
        },
        options: {
          indexAxis: horizontal ? 'y' : 'x',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: showLegend && datasets.length > 1,
              position: 'top',
              labels: {
                padding: 20,
                font: {
                  size: 14,
                  family: "'Montserrat', sans-serif"
                },
                usePointStyle: true,
                pointStyle: 'rect'
              }
            },
            title: {
              display: !!title,
              text: title,
              font: {
                size: 20,
                family: "'Montserrat', sans-serif",
                weight: '600'
              },
              padding: {
                bottom: 30
              },
              color: '#1F2937'
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
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  if (context.parsed.y !== null) {
                    label += new Intl.NumberFormat('en-US', { 
                      style: 'currency', 
                      currency: 'EUR',
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0
                    }).format(horizontal ? context.parsed.x : context.parsed.y);
                  }
                  return label;
                }
              }
            }
          },
          scales: scales || defaultScales,
          animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
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
  }, [labels, datasets, title, height, horizontal, stacked, showLegend, scales, xAxisLabel, yAxisLabel]);

  return (
    <div className={`bg-white ${className}`}>
      <div style={{ height: `${height}px` }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
};

export default BarChart;