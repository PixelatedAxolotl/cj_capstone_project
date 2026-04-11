const plotConfig = {
    responsive: true,
    modeBarButtonsToRemove: [
        'lasso2d',
        'select2d',
        'zoom2d',
        'pan2d',
        'zoomIn2d',
        'zoomOut2d',
        'autoScale2d',
        'resetScale2d']
};

// Read a CSS custom property value from the document root.
function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Convert a 6-digit hex color string to [r, g, b] integers.
function hexToRgb(hex) {
    hex = hex.trim().replace(/^#/, '');
    return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16),
    ];
}

// Build the Plotly layout override object from live CSS variables.
// Called at relayout time so it always reflects the current theme.
window.getCurrentPlotlyTheme = function() {
    const bg   = cssVar('--plotly-bg');
    const grid = cssVar('--plotly-grid');
    const text = cssVar('--text-primary');
    return {
        paper_bgcolor:     bg,
        plot_bgcolor:      bg,
        'font.color':      text,
        'xaxis.color':     text,
        'xaxis.gridcolor': grid,
        'xaxis.linecolor': grid,
        'yaxis.color':     text,
        'yaxis.gridcolor': grid,
        'yaxis.linecolor': grid,
        'legend.bgcolor':  bg,
    };
};

// Convenience: get the ordered bar color palette from CSS variables.
window.getPlotlyBarColors = function() {
    return [
        cssVar('--plotly-bar-1'),
        cssVar('--plotly-bar-2'),
        cssVar('--plotly-bar-3'),
        cssVar('--plotly-bar-4'),
    ];
};

// Apply both layout and trace colors to a single plot.
// Pass either an element ID string or a DOM element.
// Bar charts: restyles marker colors from CSS palette variables.
// Table traces: restyles header fill, cell borders, section rows, and heatmap cell shading.
window.applyPlotlyTheme = function(elOrId) {
    const el = typeof elOrId === 'string' ? document.getElementById(elOrId) : elOrId;
    if (!el) return;
    Plotly.relayout(el, window.getCurrentPlotlyTheme());

    const traces = el.data || [];
    if (traces.length === 0) return;

    if ((traces[0].type || '') === 'table') {
        const headerFill  = cssVar('--plotly-table-header');
        const sectionFill = cssVar('--plotly-table-section');
        const borderColor = cssVar('--plotly-table-border');
        const [hr, hg, hb] = hexToRgb(cssVar('--plotly-table-heatmap'));

        // Mutate el.data directly — Plotly.restyle doesn't reliably update
        // table fill colors, so we write into the live data model and redraw.
        const trace = el.data[0];
        trace.header.fill = { color: headerFill };
        trace.header.line = { color: borderColor };
        trace.cells.line  = { color: borderColor };

        // Rebase cell fill colors:
        //   rgba(...) cells are heatmap-shaded — keep alpha, swap RGB to new heatmap base.
        //   Any other non-white solid is a section header row — swap to new section color.
        //   'white' base cells use the plotly background so dark mode is respected.
        const cellBg = cssVar('--plotly-table-header');
        trace.cells.fill.color = (trace.cells.fill.color || []).map(colColors =>
            colColors.map(c => {
                if (!c || c === 'white') return cellBg;
                const m = c.match(/rgba\(\s*[\d.]+,\s*[\d.]+,\s*[\d.]+,\s*([\d.]+)\s*\)/);
                if (m) return `rgba(${hr}, ${hg}, ${hb}, ${m[1]})`;
                return sectionFill;
            })
        );
        // Use react instead of redraw — react explicitly passes the mutated data
        // back into Plotly, whereas redraw can use a stale internal cache on
        // newPlot-initialized elements.
        Plotly.react(el, el.data, el.layout);
    } else {
        const colors = window.getPlotlyBarColors();
        Plotly.restyle(el, {'marker.color': traces.map((_, i) => colors[i % colors.length])});
    }
};

// Call after creating any plot, and also wired to the theme toggle button.
window.relayoutAllPlots = function() {
    if (typeof Plotly === 'undefined') return;
    document.querySelectorAll('.js-plotly-plot').forEach(el => window.applyPlotlyTheme(el));
};
