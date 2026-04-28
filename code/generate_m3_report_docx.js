const fs = require('fs');
const path = require('path');
const {
  AlignmentType,
  BorderStyle,
  Document,
  HeadingLevel,
  ImageRun,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  VerticalAlign,
  WidthType,
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const FIGURES = path.join(ROOT, 'results', 'figures');
const TABLES = path.join(ROOT, 'results', 'tables');
const OUTPUT = path.join(ROOT, 'results', 'reports', 'M3_cross_asset_uncertainty_report.docx');

function readCsv(filePath) {
  const lines = fs.readFileSync(filePath, 'utf8').trim().split(/\r?\n/);
  const headers = lines[0].split(',');
  return lines.slice(1).filter(Boolean).map((line) => {
    const values = line.split(',');
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] ?? '';
    });
    return row;
  });
}

function textRun(text, options = {}) {
  return new TextRun({ text, font: 'Arial', size: 22, ...options });
}

function para(children, options = {}) {
  return new Paragraph({
    children,
    spacing: { after: 140, before: 0, ...options.spacing },
    ...options,
  });
}

function heading(text, level = HeadingLevel.HEADING_1, pageBreakBefore = false) {
  return new Paragraph({
    heading: level,
    pageBreakBefore,
    children: [textRun(text, { bold: true })],
    spacing: { before: 180, after: 120 },
  });
}

function imageParagraph(fileName, width, height, caption) {
  const imagePath = path.join(FIGURES, fileName);
  return [
    para([
      new ImageRun({
        type: 'png',
        data: fs.readFileSync(imagePath),
        transformation: { width, height },
        altText: {
          title: caption,
          description: caption,
          name: fileName,
        },
      }),
    ], { alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    para([
      textRun(caption, { italics: true, size: 18 }),
    ], { alignment: AlignmentType.CENTER, spacing: { after: 160 } }),
  ];
}

function simpleTable(headers, rows, widths) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: 'D0D0D0' };
  const borders = { top: border, bottom: border, left: border, right: border };

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        children: headers.map((header, index) => new TableCell({
          borders,
          width: { size: widths[index], type: WidthType.DXA },
          shading: { fill: 'E8EEF5', type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [para([textRun(header, { bold: true })], { spacing: { after: 0 } })],
        })),
      }),
      ...rows.map((row) => new TableRow({
        children: row.map((cell, index) => new TableCell({
          borders,
          width: { size: widths[index], type: WidthType.DXA },
          verticalAlign: VerticalAlign.CENTER,
          children: [para([textRun(cell)], { spacing: { after: 0 } })],
        })),
      })),
    ],
  });
}

function formatNumber(value, digits = 3) {
  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    return value;
  }
  return parsed.toFixed(digits);
}

const regressionRows = readCsv(path.join(TABLES, 'M3_regression_table.csv')).slice(0, 4);
const driverTable = simpleTable(
  ['Driver', 'Observed relationship', 'Interpretation'],
  [
    ['VIX', 'r = 0.55 with divergence', 'Strongest uncertainty correlate; supports a risk-off fragmentation channel'],
    ['Fed Funds Rate', 'r = 0.111 at the 12-month lag', 'Policy matters most with delay rather than contemporaneously'],
    ['BBB Spread', 'r = 0.48 with divergence', 'Credit stress widens dispersion through financing conditions'],
    ['Consumer Sentiment', 'r = -0.31 with divergence', 'Higher confidence tends to compress cross-asset dispersion'],
  ],
  [2100, 3300, 3960],
);

const comparisonRows = readCsv(path.join(TABLES, 'M3_modelB_ml_comparison.csv'));
const modelComparisonTable = simpleTable(
  ['Model', 'Test R2', 'Test RMSE'],
  comparisonRows.map((row) => [
    row.model,
    formatNumber(row.test_r2, 3),
    formatNumber(row.test_rmse, 3),
  ]),
  [2500, 3000, 3860],
);

const robustRows = readCsv(path.join(TABLES, 'M3_modelA_robustness_checks.csv')).filter((row) => row.robustness_type === 'RobustSEComparison');
const robustTable = simpleTable(
  ['HC spec', 'Policy coef.', 'Policy p-value', 'Policy SE'],
  robustRows.map((row) => [
    row.specification.replace('RobustSE_', ''),
    formatNumber(row.coef, 4),
    formatNumber(row.p_value, 4),
    formatNumber(row.std_err, 4),
  ]),
  [2100, 2200, 2200, 2860],
);

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: 'Arial',
          size: 22,
        },
      },
    },
    paragraphStyles: [
      {
        id: 'Heading1',
        name: 'Heading 1',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { font: 'Arial', size: 30, bold: true },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2',
        name: 'Heading 2',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { font: 'Arial', size: 26, bold: true },
        paragraph: { spacing: { before: 160, after: 100 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        para([textRun('What Drives Cross-Asset Uncertainty?', { bold: true, size: 34 })], {
          alignment: AlignmentType.CENTER,
          spacing: { before: 1200, after: 180 },
        }),
        para([textRun('Evidence from the Federal Funds Rate, VIX, and a monthly multi-asset panel', { size: 24 })], {
          alignment: AlignmentType.CENTER,
          spacing: { after: 280 },
        }),
        para([textRun('QM 2023 Capstone Project', { size: 22 })], { alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
        para([textRun('Prepared from the project’s M2 and M3 results', { size: 20, italics: true })], { alignment: AlignmentType.CENTER, spacing: { after: 420 } }),
        para([textRun('Research question', { bold: true }), textRun(': What is driving the divergence between asset classes, and how well can macroeconomic variables predict relative performance? The report’s central finding is that the strongest signals are not a single contemporaneous policy rate effect, but delayed monetary transmission and market uncertainty. In the exploratory work, VIX is the strongest bivariate correlate of divergence, while the Fed Funds Rate matters most at a 12-month lag. In the fixed-effects model, the average policy coefficient is small, but the broader pattern still points to FFR and VIX as the key economic drivers of cross-asset uncertainty.')], { spacing: { after: 180 } }),
        para([textRun('This document synthesizes the exploratory correlations, lagged patterns, group heterogeneity, and the final fixed-effects / random-forest benchmarks in a figure-forward format so the interpretation stays anchored to the visuals.', { size: 22 })], { spacing: { after: 180 } }),
        heading('Executive Summary', HeadingLevel.HEADING_1, true),
        para([textRun('The cleanest read from the project is that uncertainty widens the spread between asset classes, while policy works through time-lagged channels rather than a large same-month effect. The exploratory heatmap shows VIX as the strongest correlate of the divergence index, and the lag plot shows the 12-month Fed Funds relationship becoming more informative than the contemporaneous rate. That combination suggests the system responds to both market stress and delayed policy transmission.', { size: 22 })]),
        para([textRun('The final M3 fixed-effects specification reinforces that interpretation. The lagged policy term is economically small and statistically insignificant on average, while the VIX exposure term is also small after conditioning on fixed effects. That does not mean the variables are irrelevant; it means the average linear coefficient is weak once time effects, asset effects, and return dynamics are all controlled. The behavior is therefore better described as heterogeneous and regime-sensitive than as a single common slope.', { size: 22 })]),
        para([textRun('A secondary conclusion is that predictive accuracy and interpretability point in different directions. Random Forest slightly outperforms OLS on the held-out test set, but the fixed-effects model is the better vehicle for economic interpretation. In other words, the report uses the machine-learning benchmark as a predictive check, not as the final causal story.', { size: 22 })]),
        heading('Research Design and Key Drivers', HeadingLevel.HEADING_1, true),
        para([textRun('The panel combines monthly data for stocks, housing, gold, and bitcoin with macro-financial controls such as the Federal Funds Rate, VIX, BBB spreads, consumer sentiment, inflation, and policy uncertainty. The project’s divergence measure captures how far the asset classes move away from one another over time, which makes it a direct proxy for cross-asset uncertainty and dispersion.', { size: 22 })]),
        para([textRun('The table below summarizes the driver relationships that shaped the final specification. VIX stands out as the most direct uncertainty proxy, while the Fed Funds Rate becomes most informative only after a delay. Credit stress and sentiment move in the expected directions as well, but the report focuses on FFR and VIX because they anchor the policy and uncertainty channels that survive across the EDA and M3 stages.', { size: 22 })]),
        driverTable,
        para([textRun('The important implication is that policy should not be interpreted as a contemporaneous shock alone. The asset panel suggests that rates influence dispersion through refinancing, balance-sheet adjustment, and portfolio reweighting, all of which take time. VIX, by contrast, is closer to the surface of the system: it captures stress as it is happening and therefore aligns tightly with immediate widening in cross-asset dispersion.', { size: 22 })]),
        heading('Exploratory Evidence', HeadingLevel.HEADING_1, true),
        para([textRun('The correlation heatmap is the simplest summary of the project’s first-stage evidence. VIX is the strongest control correlate of divergence, which is why it became the anchor risk variable in M3. The same map also supports the role of credit stress and sentiment, but their relationships are weaker and less central to the report’s final narrative than uncertainty itself.', { size: 22 })]),
        ...imageParagraph('M2_plot1_correlation_heatmap.png', 620, 360, 'Figure 1. Correlation heatmap: VIX is the strongest bivariate correlate of divergence, with policy and credit measures also visible but weaker.'),
        para([textRun('The outcome time series shows that high-divergence episodes cluster in stress windows rather than being evenly distributed through the sample. This is important because it means the phenomenon is not just a slow trend; it is regime-driven. The timing of the largest spikes lines up with periods where uncertainty and policy pressure were both elevated, which is exactly the pattern that motivates the later fixed-effects and robustness checks.', { size: 22 })]),
        ...imageParagraph('M2_plot2_outcome_timeseries.png', 620, 340, 'Figure 2. Divergence index over time: the largest spikes concentrate in crisis and stress periods.'),
        para([textRun('The lag plot addresses the policy-timing question directly. The strongest policy relationship does not appear at zero lag. Instead, the 12-month Fed Funds lag becomes the most informative horizon, which is consistent with delayed transmission through household, corporate, and portfolio adjustment channels. That is the main reason the final specification uses a lagged policy term rather than relying on contemporaneous rates alone.', { size: 22 })]),
        ...imageParagraph('M2_plot4_lagged_effects.png', 620, 350, 'Figure 3. Lagged effects plot: the 12-month policy horizon is more informative than shorter lags.'),
        heading('Policy and Uncertainty Channels', HeadingLevel.HEADING_1, true),
        para([textRun('The dual-axis plot puts the divergence series and the Federal Funds Rate on the same timeline. The visual takeaway is not that they move in lockstep month to month, but that the policy regime helps frame the dispersion regime. Rate changes are part of the story, yet the link is delayed and indirect, so the rate line is more useful as a regime marker than as a contemporaneous prediction signal.', { size: 22 })]),
        ...imageParagraph('M2_plot3_dual_axis_divergence_fedfunds.png', 620, 360, 'Figure 4. Divergence and the Federal Funds Rate across policy regimes: timing matters more than same-month co-movement.'),
        para([textRun('The paired scatterplots make the risk channel more explicit. Divergence rises with VIX and falls with consumer sentiment, which is the cleanest visual evidence that uncertainty widens dispersion while confidence compresses it. Because the VIX slope is positive and the sentiment slope is negative, the two variables act as opposite sides of the same macro-financial risk spectrum.', { size: 22 })]),
        ...imageParagraph('M2_plot7_factor_scatterplots.png', 620, 360, 'Figure 5. Factor scatterplots: VIX slopes upward with divergence, while consumer sentiment slopes downward.'),
        para([textRun('Group sensitivity adds another layer. Housing is the most rate-sensitive asset class, gold behaves as the most rate-resilient, and equities sit closer to the middle. That heterogeneity matters because it explains why a single policy coefficient does not cleanly summarize the panel. The report therefore interprets policy through interaction and regime language rather than through a uniform slope applied to every asset class.', { size: 22 })]),
        ...imageParagraph('M2_plot6_group_sensitivity.png', 620, 340, 'Figure 6. Asset-class sensitivity to the Federal Funds Rate: housing is the most rate-sensitive group.'),
        heading('M3 Results and Diagnostics', HeadingLevel.HEADING_1, true),
        para([textRun('The final fixed-effects model keeps the interpretation conservative. The lagged policy exposure coefficient is approximately -0.0029 and the VIX exposure coefficient is approximately -0.0040, both small in magnitude after fixed effects are included. The stronger signals in the model are the dynamic terms, especially the lagged return and 3-month momentum terms, which confirms that persistence and short-horizon reversal dominate the response structure more than a simple direct policy effect.', { size: 22 })]),
        simpleTable(
          ['Term', 'Coef.', 'SE', 'p-value'],
          regressionRows.map((row) => [
            row.term,
            formatNumber(row.coef, 4),
            formatNumber(row.std_err, 4),
            formatNumber(row.p_value, 4),
          ]),
          [3400, 2000, 2000, 1960],
        ),
        para([textRun('The diagnostic plots indicate why robust inference matters. The Breusch-Pagan test is significant, so standard errors should not be treated as homoskedastic by default. The residuals-vs-fitted plot is broadly centered but still shows structure, and the Q-Q plot suggests the usual tail deviations that are common in monthly financial panels.', { size: 22 })]),
        ...imageParagraph('M3_residuals_vs_fitted.png', 590, 330, 'Figure 7. Residuals versus fitted values: the fitted pattern supports robust inference.'),
        ...imageParagraph('M3_qq_plot.png', 590, 330, 'Figure 8. Q-Q plot: tail departures motivate heteroskedasticity-robust standard errors.'),
        para([textRun('The robustness comparison shows that the policy estimate remains stable across HC specifications, which is a useful sanity check even though the coefficient itself is not significant. The more important point is that the sign and scale do not swing wildly across covariance estimators, so the conclusion is not an artifact of one particular standard-error choice.', { size: 22 })]),
        robustTable,
        ...imageParagraph('M3_modelA_robust_se_comparison.png', 620, 330, 'Figure 9. Robust standard-error comparison: the policy estimate stays stable across HC variants.'),
        heading('Predictive Benchmark and Interpretation', HeadingLevel.HEADING_1, true),
        para([textRun('Random Forest provides a modestly better held-out fit than OLS, which is consistent with the presence of nonlinear interactions and regime effects. The model is not presented as the final economic explanation; it is a benchmark showing that the panel contains structure beyond a plain linear average response.', { size: 22 })]),
        modelComparisonTable,
        ...imageParagraph('M3_modelB_rf_feature_importance_top10.png', 620, 360, 'Figure 10. Random Forest feature importance: dynamic return terms dominate prediction, with VIX still visible.'),
        para([textRun('Taken together, the predictive and causal views point to the same practical conclusion. FFR matters because policy influences asset pricing with a delay, and VIX matters because uncertainty immediately widens cross-asset dispersion. The cleanest summary of the report is therefore that cross-asset uncertainty is driven by the interaction of delayed policy transmission and contemporaneous market stress, not by a single instantaneous policy rate effect.', { size: 22 })]),
        heading('Conclusion', HeadingLevel.HEADING_1, true),
        para([textRun('If the question is what drives cross-asset uncertainty, the answer from this project is that the Federal Funds Rate and VIX are the most important organizing variables, but they act on different clocks. The Federal Funds Rate shows up most clearly through lagged transmission, while VIX captures immediate risk-off pressure. That combination is what produces the strongest and most persistent divergence across assets.', { size: 22 })]),
        para([textRun('For presentation purposes, the report is intentionally figure-heavy so the interpretation stays tied to the evidence. The visuals consistently show the same story: VIX is the strongest uncertainty correlate, policy is delayed, and the panel responds heterogeneously across asset classes. Those are the findings that matter most for the final capstone narrative.', { size: 22 })]),
      ],
    },
  ],
});

async function main() {
  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUTPUT, buffer);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});