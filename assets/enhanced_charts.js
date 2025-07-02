// Custom chart template for all Plotly graphs
const getChartTemplate = () => {
  // Check if dark mode is enabled
  const isDarkMode = document.body.classList.contains('dark-mode');
  
  // Enhanced vibrant colors for both light and dark modes
  const vibrantColors = [
    '#4051b5', // Blue
    '#e91e63', // Pink
    '#00c853', // Green
    '#ff9800', // Orange
    '#9c27b0', // Purple
    '#00b0ff', // Light Blue
    '#ffab00', // Amber
    '#6200ea', // Deep Purple
    '#c51162', // Pink Accent
    '#00bfa5'  // Teal Accent
  ];
  
  // Even more saturated colors for dark mode
  const darkModeColors = [
    '#4361ee', // Indigo
    '#f72585', // Pink
    '#06d6a0', // Green
    '#ffd166', // Amber
    '#7209b7', // Purple
    '#00b4d8', // Cyan
    '#f94144', // Red
    '#4cc9f0', // Bright Blue
    '#f15bb5', // Hot Pink
    '#9b5de5'  // Purple
  ];
  
  return {
    layout: {
      colorway: isDarkMode ? darkModeColors : vibrantColors,
      paper_bgcolor: isDarkMode ? '#16213e' : '#ffffff',
      plot_bgcolor: isDarkMode ? '#16213e' : '#ffffff',
      font: {
        family: 'Inter, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        size: 12,
        color: isDarkMode ? '#e0e0e0' : '#2c3e50'
      },
      title: {
        font: {
          family: 'Roboto, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif',
          size: 18,
          color: isDarkMode ? '#ffffff' : '#1a1a1a'
        },
        x: 0.01 // Left align title
      },
      margin: {
        l: 50,
        r: 20,
        t: 50,
        b: 50
      },
      hovermode: 'closest',
      hoverlabel: {
        bgcolor: isDarkMode ? '#222f5b' : '#ffffff',
        font: { color: isDarkMode ? '#e0e0e0' : '#2c3e50' },
        bordercolor: isDarkMode ? '#4361ee' : '#4051b5'
      },
      xaxis: {
        gridcolor: isDarkMode ? 'rgba(48, 71, 94, 0.3)' : 'rgba(233, 236, 239, 0.5)',
        linecolor: isDarkMode ? '#30475e' : '#e9ecef',
        showgrid: true,
        zeroline: false,
        title: {
          font: {
            family: 'Inter, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 14,
            color: isDarkMode ? '#e6e6e6' : '#2c3e50'
          },
          standoff: 10
        },
        color: isDarkMode ? '#e6e6e6' : '#2c3e50'
      },
      yaxis: {
        gridcolor: isDarkMode ? 'rgba(48, 71, 94, 0.3)' : 'rgba(233, 236, 239, 0.5)',
        linecolor: isDarkMode ? '#30475e' : '#e9ecef',
        showgrid: true,
        zeroline: false,
        title: {
          font: {
            family: 'Inter, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            size: 14,
            color: isDarkMode ? '#e6e6e6' : '#2c3e50'
          },
          standoff: 10
        },
        color: isDarkMode ? '#e6e6e6' : '#2c3e50'
      },
      legend: {
        font: {
          family: 'Inter, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          size: 12,
          color: isDarkMode ? '#e0e0e0' : '#2c3e50'
        },
        bgcolor: isDarkMode ? 'rgba(22, 33, 62, 0.5)' : 'rgba(255, 255, 255, 0.5)',
        bordercolor: isDarkMode ? '#30475e' : '#e9ecef'
      }
    }
  };
};

// Apply template to all Plotly charts
window.Plotly.setPlotConfig({
  mapboxAccessToken: undefined,
  plotlyServerURL: undefined,
  responsive: true
});

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    applyTemplate: function(figure) {
      if (figure && figure.layout) {
        const updatedFigure = JSON.parse(JSON.stringify(figure)); // Deep copy
        updatedFigure.layout = Object.assign({}, getChartTemplate().layout, figure.layout);
        return updatedFigure;
      }
      return figure;
    }
  }
});

// Function to apply template to all graphs
const applyTemplateToGraphs = () => {
  const template = getChartTemplate();
  
  // Apply to all graphs
  const graphDivs = document.querySelectorAll('.js-plotly-plot');
  graphDivs.forEach(div => {
    try {
      const graphDiv = div;
      if (graphDiv._fullLayout) {
        const newLayout = {
          colorway: template.layout.colorway,
          paper_bgcolor: template.layout.paper_bgcolor,
          plot_bgcolor: template.layout.plot_bgcolor,
          font: template.layout.font,
          xaxis: {
            gridcolor: template.layout.xaxis.gridcolor,
            linecolor: template.layout.xaxis.linecolor,
            color: template.layout.xaxis.color
          },
          yaxis: {
            gridcolor: template.layout.yaxis.gridcolor,
            linecolor: template.layout.yaxis.linecolor,
            color: template.layout.yaxis.color
          }
        };
        
        window.Plotly.relayout(graphDiv, newLayout);
      }
    } catch (e) {
      console.error('Error updating graph template:', e);
    }
  });
};

// Listen for theme changes to update charts
const observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.attributeName === 'class') {
      // When body class changes (dark mode toggle), update all charts
      setTimeout(() => {
        applyTemplateToGraphs();
        window.dispatchEvent(new Event('resize'));
      }, 100);
    }
  });
});

// Update graphs when window is resized
window.addEventListener('resize', () => {
  setTimeout(applyTemplateToGraphs, 100);
});

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', function() {
  observer.observe(document.body, { attributes: true });
  setTimeout(applyTemplateToGraphs, 500);
});
