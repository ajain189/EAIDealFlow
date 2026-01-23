import { CompanyResearch } from '../types';

// Industry benchmarks for valuation
const INDUSTRY_BENCHMARKS: Record<string, { ebitdaMultiple: number; revenueMultiple: number; avgMargin: number }> = {
  'HVAC': { ebitdaMultiple: 5.2, revenueMultiple: 0.9, avgMargin: 15 },
  'Transportation': { ebitdaMultiple: 4.8, revenueMultiple: 0.7, avgMargin: 12 },
  'Manufacturing': { ebitdaMultiple: 5.5, revenueMultiple: 0.8, avgMargin: 14 },
  'Technology': { ebitdaMultiple: 8.2, revenueMultiple: 2.5, avgMargin: 22 },
  'Healthcare': { ebitdaMultiple: 7.0, revenueMultiple: 1.8, avgMargin: 18 },
  'Construction': { ebitdaMultiple: 4.2, revenueMultiple: 0.5, avgMargin: 10 },
  'Retail': { ebitdaMultiple: 3.8, revenueMultiple: 0.4, avgMargin: 8 },
  'Professional Services': { ebitdaMultiple: 6.5, revenueMultiple: 1.2, avgMargin: 20 },
  'default': { ebitdaMultiple: 5.0, revenueMultiple: 0.8, avgMargin: 14 },
};

// Estimate metrics from company data
function estimateMetrics(company: CompanyResearch) {
  const employeeStr = company.employeeCount?.toLowerCase() || '';
  let employees = 50;

  if (employeeStr.includes('1000') || employeeStr.includes('1,000')) employees = 1000;
  else if (employeeStr.includes('500')) employees = 500;
  else if (employeeStr.includes('200')) employees = 200;
  else if (employeeStr.includes('100')) employees = 100;
  else if (employeeStr.includes('50')) employees = 50;
  else if (employeeStr.includes('20') || employeeStr.includes('25')) employees = 25;
  else if (employeeStr.includes('10')) employees = 15;

  const benchmark = INDUSTRY_BENCHMARKS[company.industry] || INDUSTRY_BENCHMARKS['default'];
  const revenuePerEmployee = 150000 + (benchmark.avgMargin / 100) * 100000;
  const estimatedRevenue = (employees * revenuePerEmployee) / 1000000; // in millions
  const estimatedEbitda = estimatedRevenue * (benchmark.avgMargin / 100);

  return {
    employees,
    estimatedRevenue: Math.round(estimatedRevenue * 10) / 10,
    estimatedEbitda: Math.round(estimatedEbitda * 10) / 10,
    ebitdaMargin: benchmark.avgMargin,
    ebitdaMultiple: benchmark.ebitdaMultiple,
    revenueMultiple: benchmark.revenueMultiple,
    lowValuation: Math.round(estimatedEbitda * benchmark.ebitdaMultiple * 0.8 * 10) / 10,
    midValuation: Math.round(estimatedEbitda * benchmark.ebitdaMultiple * 10) / 10,
    highValuation: Math.round(estimatedEbitda * benchmark.ebitdaMultiple * 1.2 * 10) / 10,
  };
}

// Calculate deal heat score based on company attributes
function calculateDealHeat(company: CompanyResearch): { score: number; factors: string[] } {
  let score = 50;
  const factors: string[] = [];

  // Industry attractiveness
  const hotIndustries = ['Technology', 'Healthcare', 'Professional Services'];
  if (hotIndustries.includes(company.industry)) {
    score += 15;
    factors.push('High-growth industry sector');
  }

  // Competitive moat
  const competitive = company.competitiveAdvantage?.toLowerCase() || '';
  if (competitive.includes('leading') || competitive.includes('dominant') || competitive.includes('#1')) {
    score += 20;
    factors.push('Strong market leadership position');
  } else if (competitive.includes('established') || competitive.includes('proven')) {
    score += 10;
    factors.push('Established market presence');
  }

  // Employee count (scale indicator)
  const employeeStr = company.employeeCount?.toLowerCase() || '';
  if (employeeStr.includes('100') || employeeStr.includes('200') || employeeStr.includes('500')) {
    score += 10;
    factors.push('Meaningful operational scale');
  }

  // Ownership clarity
  if (company.ownershipHints && company.ownershipHints !== 'Not publicly available') {
    score += 5;
    factors.push('Clear ownership structure');
  }

  // Service diversification
  if (company.services.length >= 4) {
    score += 10;
    factors.push('Diversified service offering');
  }

  return { score: Math.min(100, score), factors };
}

// Generate SWOT analysis
function generateSWOT(company: CompanyResearch, metrics: ReturnType<typeof estimateMetrics>) {
  const strengths = [
    company.competitiveAdvantage || 'Established market position',
    company.services.length > 2 ? 'Diversified service portfolio' : 'Focused service expertise',
    company.yearFounded && company.yearFounded !== 'Unknown' ?
      `${new Date().getFullYear() - parseInt(company.yearFounded)} years of operational history` :
      'Track record in the market',
  ];

  const weaknesses = [
    'Limited public financial data available',
    metrics.estimatedRevenue < 20 ? 'Sub-scale revenue base' : 'May require growth capital',
    'Potential key-person dependency',
  ];

  const opportunities = [
    `Industry consolidation in ${company.industry} sector`,
    'Geographic expansion potential',
    'Add-on acquisition opportunities',
    'Operational efficiency improvements',
  ];

  const threats = [
    'Competitive pressure from larger players',
    'Economic cycle sensitivity',
    `${company.industry} regulatory changes`,
    'Labor market tightness',
  ];

  return { strengths, weaknesses, opportunities, threats };
}

export function generatePDFHTML(company: CompanyResearch): string {
  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const metrics = estimateMetrics(company);
  const dealHeat = calculateDealHeat(company);
  const swot = generateSWOT(company, metrics);
  const benchmark = INDUSTRY_BENCHMARKS[company.industry] || INDUSTRY_BENCHMARKS['default'];

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #1a1a2e;
      background: #ffffff;
      font-size: 11px;
      line-height: 1.5;
    }

    .page {
      padding: 40px;
      max-width: 850px;
      margin: 0 auto;
    }

    /* Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding-bottom: 20px;
      border-bottom: 2px solid #1a1a2e;
      margin-bottom: 24px;
    }

    .logo-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-mark {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 700;
      font-size: 14px;
    }

    .logo-text {
      display: flex;
      flex-direction: column;
    }

    .logo {
      font-family: 'Playfair Display', serif;
      font-size: 20px;
      font-weight: 700;
      color: #1a1a2e;
      letter-spacing: -0.5px;
    }

    .logo-subtitle {
      font-size: 10px;
      color: #64748b;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .header-right {
      text-align: right;
    }

    .report-type {
      font-size: 9px;
      font-weight: 600;
      color: #6366f1;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-bottom: 4px;
    }

    .date {
      font-size: 10px;
      color: #64748b;
    }

    /* Company Title Section */
    .company-title-section {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid #e2e8f0;
    }

    .company-info {
      flex: 1;
    }

    .company-name {
      font-family: 'Playfair Display', serif;
      font-size: 28px;
      font-weight: 700;
      color: #1a1a2e;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }

    .company-meta {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      align-items: center;
    }

    .meta-tag {
      background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
      color: #4f46e5;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 10px;
      font-weight: 600;
    }

    .meta-item {
      font-size: 10px;
      color: #64748b;
    }

    /* Deal Heat Thermometer */
    .deal-heat-box {
      width: 160px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      text-align: center;
    }

    .heat-label {
      font-size: 9px;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .heat-score {
      font-size: 32px;
      font-weight: 700;
      color: ${dealHeat.score >= 70 ? '#10b981' : dealHeat.score >= 50 ? '#f59e0b' : '#64748b'};
      line-height: 1;
    }

    .heat-bar {
      width: 100%;
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      margin-top: 8px;
      overflow: hidden;
    }

    .heat-fill {
      height: 100%;
      width: ${dealHeat.score}%;
      background: linear-gradient(90deg,
        ${dealHeat.score >= 70 ? '#10b981' : dealHeat.score >= 50 ? '#f59e0b' : '#94a3b8'} 0%,
        ${dealHeat.score >= 70 ? '#34d399' : dealHeat.score >= 50 ? '#fbbf24' : '#cbd5e1'} 100%);
      border-radius: 3px;
    }

    .heat-status {
      font-size: 9px;
      color: ${dealHeat.score >= 70 ? '#10b981' : dealHeat.score >= 50 ? '#f59e0b' : '#64748b'};
      font-weight: 600;
      margin-top: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Dashboard Grid */
    .dashboard-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }

    .dashboard-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e2e8f0;
    }

    .card-title {
      font-size: 10px;
      font-weight: 600;
      color: #1a1a2e;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }

    .card-badge {
      font-size: 8px;
      font-weight: 600;
      color: #6366f1;
      background: #eef2ff;
      padding: 2px 8px;
      border-radius: 8px;
    }

    /* Valuation Section */
    .valuation-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .val-box {
      text-align: center;
      padding: 12px 8px;
      background: white;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
    }

    .val-box.highlight {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border: none;
    }

    .val-box.highlight .val-label,
    .val-box.highlight .val-amount {
      color: white;
    }

    .val-label {
      font-size: 8px;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .val-amount {
      font-size: 18px;
      font-weight: 700;
      color: #1a1a2e;
    }

    .val-suffix {
      font-size: 10px;
      font-weight: 500;
    }

    /* Metrics Grid */
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 12px;
    }

    .metric-mini {
      text-align: center;
      padding: 10px 6px;
      background: white;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }

    .metric-mini-label {
      font-size: 8px;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      margin-bottom: 2px;
    }

    .metric-mini-value {
      font-size: 12px;
      font-weight: 600;
      color: #1a1a2e;
    }

    /* SWOT Grid */
    .swot-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .swot-box {
      padding: 10px;
      border-radius: 8px;
      font-size: 9px;
    }

    .swot-box.strengths {
      background: #ecfdf5;
      border-left: 3px solid #10b981;
    }

    .swot-box.weaknesses {
      background: #fef2f2;
      border-left: 3px solid #ef4444;
    }

    .swot-box.opportunities {
      background: #eff6ff;
      border-left: 3px solid #3b82f6;
    }

    .swot-box.threats {
      background: #fefce8;
      border-left: 3px solid #eab308;
    }

    .swot-title {
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }

    .swot-box.strengths .swot-title { color: #059669; }
    .swot-box.weaknesses .swot-title { color: #dc2626; }
    .swot-box.opportunities .swot-title { color: #2563eb; }
    .swot-box.threats .swot-title { color: #ca8a04; }

    .swot-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .swot-list li {
      padding: 2px 0;
      padding-left: 10px;
      position: relative;
      color: #374151;
      line-height: 1.4;
    }

    .swot-list li::before {
      content: '•';
      position: absolute;
      left: 0;
      color: #9ca3af;
    }

    /* Full Width Sections */
    .full-section {
      margin-bottom: 24px;
    }

    .section-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }

    .section-icon {
      width: 24px;
      height: 24px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 12px;
    }

    .section-title {
      font-size: 12px;
      font-weight: 700;
      color: #1a1a2e;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Thesis Box */
    .thesis-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .thesis-box {
      padding: 16px;
      border-radius: 10px;
    }

    .thesis-box.buy {
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
      border: 1px solid #a7f3d0;
    }

    .thesis-box.risk {
      background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
      border: 1px solid #fecaca;
    }

    .thesis-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .thesis-box.buy .thesis-title { color: #059669; }
    .thesis-box.risk .thesis-title { color: #dc2626; }

    .thesis-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .thesis-list li {
      padding: 4px 0;
      padding-left: 16px;
      position: relative;
      font-size: 10px;
      color: #374151;
      line-height: 1.5;
    }

    .thesis-box.buy .thesis-list li::before {
      content: '+';
      position: absolute;
      left: 0;
      font-weight: 700;
      color: #10b981;
    }

    .thesis-box.risk .thesis-list li::before {
      content: '!';
      position: absolute;
      left: 2px;
      font-weight: 700;
      color: #ef4444;
    }

    /* Services List */
    .services-compact {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }

    .service-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 10px;
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      font-size: 10px;
      color: #374151;
    }

    .service-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      flex-shrink: 0;
    }

    /* Valuation Methodology */
    .methodology-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 16px;
      margin-top: 16px;
    }

    .methodology-title {
      font-size: 10px;
      font-weight: 700;
      color: #1a1a2e;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .methodology-table {
      width: 100%;
      border-collapse: collapse;
    }

    .methodology-table th,
    .methodology-table td {
      padding: 8px 10px;
      text-align: left;
      font-size: 10px;
      border-bottom: 1px solid #e2e8f0;
    }

    .methodology-table th {
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-size: 8px;
    }

    .methodology-table td {
      color: #1a1a2e;
    }

    .methodology-table tr:last-child td {
      border-bottom: none;
      font-weight: 600;
      color: #6366f1;
    }

    /* Footer */
    .footer {
      margin-top: 32px;
      padding-top: 16px;
      border-top: 2px solid #1a1a2e;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .footer-left {
      font-size: 8px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .footer-right {
      font-size: 9px;
      color: #64748b;
    }

    /* Benchmark Comparison */
    .benchmark-row {
      display: flex;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #f1f5f9;
    }

    .benchmark-row:last-child {
      border-bottom: none;
    }

    .benchmark-label {
      flex: 1;
      font-size: 9px;
      color: #64748b;
    }

    .benchmark-bar-container {
      flex: 2;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .benchmark-bar {
      flex: 1;
      height: 8px;
      background: #e2e8f0;
      border-radius: 4px;
      overflow: hidden;
    }

    .benchmark-fill {
      height: 100%;
      border-radius: 4px;
    }

    .benchmark-value {
      width: 50px;
      text-align: right;
      font-size: 10px;
      font-weight: 600;
      color: #1a1a2e;
    }
  </style>
</head>
<body>
  <div class="page">
    <!-- Header -->
    <div class="header">
      <div class="logo-section">
        <div class="logo-mark">EAI</div>
        <div class="logo-text">
          <div class="logo">EAI Capital</div>
          <div class="logo-subtitle">Investment Research</div>
        </div>
      </div>
      <div class="header-right">
        <div class="report-type">Confidential Valuation Snapshot</div>
        <div class="date">${currentDate}</div>
      </div>
    </div>

    <!-- Company Title + Deal Heat -->
    <div class="company-title-section">
      <div class="company-info">
        <h1 class="company-name">${company.name}</h1>
        <div class="company-meta">
          <span class="meta-tag">${company.industry}</span>
          ${company.location && company.location !== 'Unknown' ? `<span class="meta-item">${company.location}</span>` : ''}
          ${company.yearFounded && company.yearFounded !== 'Unknown' ? `<span class="meta-item">Est. ${company.yearFounded}</span>` : ''}
          ${company.employeeCount && company.employeeCount !== 'Unknown' ? `<span class="meta-item">${company.employeeCount} employees</span>` : ''}
        </div>
      </div>
      <div class="deal-heat-box">
        <div class="heat-label">Deal Heat Score</div>
        <div class="heat-score">${dealHeat.score}</div>
        <div class="heat-bar"><div class="heat-fill"></div></div>
        <div class="heat-status">${dealHeat.score >= 70 ? 'High Priority' : dealHeat.score >= 50 ? 'Moderate Interest' : 'Monitor'}</div>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div class="dashboard-grid">
      <!-- Valuation Card -->
      <div class="dashboard-card">
        <div class="card-header">
          <span class="card-title">Implied Valuation Range</span>
          <span class="card-badge">${metrics.ebitdaMultiple}x EBITDA</span>
        </div>
        <div class="valuation-grid">
          <div class="val-box">
            <div class="val-label">Conservative</div>
            <div class="val-amount">$${metrics.lowValuation}<span class="val-suffix">M</span></div>
          </div>
          <div class="val-box highlight">
            <div class="val-label">Base Case</div>
            <div class="val-amount">$${metrics.midValuation}<span class="val-suffix">M</span></div>
          </div>
          <div class="val-box">
            <div class="val-label">Optimistic</div>
            <div class="val-amount">$${metrics.highValuation}<span class="val-suffix">M</span></div>
          </div>
        </div>
        <div class="metrics-row">
          <div class="metric-mini">
            <div class="metric-mini-label">Est. Revenue</div>
            <div class="metric-mini-value">$${metrics.estimatedRevenue}M</div>
          </div>
          <div class="metric-mini">
            <div class="metric-mini-label">Est. EBITDA</div>
            <div class="metric-mini-value">$${metrics.estimatedEbitda}M</div>
          </div>
          <div class="metric-mini">
            <div class="metric-mini-label">EBITDA Margin</div>
            <div class="metric-mini-value">${metrics.ebitdaMargin}%</div>
          </div>
          <div class="metric-mini">
            <div class="metric-mini-label">Employees</div>
            <div class="metric-mini-value">${metrics.employees}</div>
          </div>
        </div>
      </div>

      <!-- SWOT Card -->
      <div class="dashboard-card">
        <div class="card-header">
          <span class="card-title">SWOT Analysis</span>
          <span class="card-badge">Quick View</span>
        </div>
        <div class="swot-grid">
          <div class="swot-box strengths">
            <div class="swot-title">Strengths</div>
            <ul class="swot-list">
              ${swot.strengths.slice(0, 2).map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
          <div class="swot-box weaknesses">
            <div class="swot-title">Weaknesses</div>
            <ul class="swot-list">
              ${swot.weaknesses.slice(0, 2).map(w => `<li>${w}</li>`).join('')}
            </ul>
          </div>
          <div class="swot-box opportunities">
            <div class="swot-title">Opportunities</div>
            <ul class="swot-list">
              ${swot.opportunities.slice(0, 2).map(o => `<li>${o}</li>`).join('')}
            </ul>
          </div>
          <div class="swot-box threats">
            <div class="swot-title">Threats</div>
            <ul class="swot-list">
              ${swot.threats.slice(0, 2).map(t => `<li>${t}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Thesis Section -->
    <div class="full-section">
      <div class="section-header">
        <div class="section-icon">T</div>
        <span class="section-title">Investment Thesis</span>
      </div>
      <div class="thesis-grid">
        <div class="thesis-box buy">
          <div class="thesis-title">
            <span>Buy Thesis</span>
          </div>
          <ul class="thesis-list">
            <li>${company.competitiveAdvantage || 'Established market position'}</li>
            ${dealHeat.factors.slice(0, 2).map(f => `<li>${f}</li>`).join('')}
            <li>Platform for add-on acquisitions in fragmented ${company.industry} market</li>
          </ul>
        </div>
        <div class="thesis-box risk">
          <div class="thesis-title">
            <span>Key Risks</span>
          </div>
          <ul class="thesis-list">
            <li>Limited financial transparency - requires detailed due diligence</li>
            <li>Potential customer concentration risk</li>
            <li>Integration complexity in potential add-on strategy</li>
            <li>Economic sensitivity of ${company.industry} sector</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Company Overview -->
    <div class="full-section">
      <div class="section-header">
        <div class="section-icon">C</div>
        <span class="section-title">Company Overview</span>
      </div>
      <div class="dashboard-card" style="background: white;">
        <p style="font-size: 11px; color: #374151; line-height: 1.7; margin-bottom: 16px;">${company.description}</p>
        <div class="services-compact">
          ${company.services.map(s => `
            <div class="service-tag">
              <div class="service-dot"></div>
              <span>${s}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Valuation Methodology -->
    <div class="full-section">
      <div class="section-header">
        <div class="section-icon">V</div>
        <span class="section-title">Valuation Methodology</span>
      </div>
      <div class="methodology-box">
        <div class="methodology-title">Comparable Transaction Analysis - ${company.industry} Sector</div>
        <table class="methodology-table">
          <tr>
            <th>Metric</th>
            <th>Target (Est.)</th>
            <th>Industry Avg</th>
            <th>Multiple Applied</th>
            <th>Implied Value</th>
          </tr>
          <tr>
            <td>Revenue</td>
            <td>$${metrics.estimatedRevenue}M</td>
            <td>$25-75M</td>
            <td>${metrics.revenueMultiple}x</td>
            <td>$${(metrics.estimatedRevenue * metrics.revenueMultiple).toFixed(1)}M</td>
          </tr>
          <tr>
            <td>EBITDA</td>
            <td>$${metrics.estimatedEbitda}M</td>
            <td>${benchmark.avgMargin}% margin</td>
            <td>${metrics.ebitdaMultiple}x</td>
            <td>$${metrics.midValuation}M</td>
          </tr>
          <tr>
            <td colspan="4"><strong>Blended Enterprise Value (Midpoint)</strong></td>
            <td><strong>$${metrics.midValuation}M</strong></td>
          </tr>
        </table>
      </div>
    </div>

    <!-- Industry Benchmarks -->
    <div class="dashboard-card" style="margin-bottom: 24px;">
      <div class="card-header">
        <span class="card-title">Industry Benchmark Comparison</span>
        <span class="card-badge">${company.industry}</span>
      </div>
      <div class="benchmark-row">
        <div class="benchmark-label">EBITDA Margin</div>
        <div class="benchmark-bar-container">
          <div class="benchmark-bar">
            <div class="benchmark-fill" style="width: ${(metrics.ebitdaMargin / 30) * 100}%; background: linear-gradient(90deg, #6366f1, #8b5cf6);"></div>
          </div>
          <div class="benchmark-value">${metrics.ebitdaMargin}%</div>
        </div>
      </div>
      <div class="benchmark-row">
        <div class="benchmark-label">Revenue Multiple</div>
        <div class="benchmark-bar-container">
          <div class="benchmark-bar">
            <div class="benchmark-fill" style="width: ${(metrics.revenueMultiple / 3) * 100}%; background: linear-gradient(90deg, #10b981, #34d399);"></div>
          </div>
          <div class="benchmark-value">${metrics.revenueMultiple}x</div>
        </div>
      </div>
      <div class="benchmark-row">
        <div class="benchmark-label">EBITDA Multiple</div>
        <div class="benchmark-bar-container">
          <div class="benchmark-bar">
            <div class="benchmark-fill" style="width: ${(metrics.ebitdaMultiple / 10) * 100}%; background: linear-gradient(90deg, #f59e0b, #fbbf24);"></div>
          </div>
          <div class="benchmark-value">${metrics.ebitdaMultiple}x</div>
        </div>
      </div>
    </div>

    ${company.keyMetrics && company.keyMetrics.length > 0 && company.keyMetrics[0] ? `
    <!-- Key Highlights -->
    <div class="dashboard-card" style="margin-bottom: 24px;">
      <div class="card-header">
        <span class="card-title">Key Research Highlights</span>
      </div>
      <div class="services-compact">
        ${company.keyMetrics.filter(m => m).map(m => `
          <div class="service-tag">
            <div class="service-dot" style="background: #10b981;"></div>
            <span>${m}</span>
          </div>
        `).join('')}
      </div>
    </div>
    ` : ''}

    <!-- Footer -->
    <div class="footer">
      <div class="footer-left">Confidential - For Discussion Purposes Only - Not Investment Advice</div>
      <div class="footer-right">Generated by EAI DealFlow Terminal</div>
    </div>
  </div>
</body>
</html>`;
}

export async function generatePDF(company: CompanyResearch): Promise<string> {
  const html = generatePDFHTML(company);

  // Create a new window for printing
  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    throw new Error('Failed to open print window');
  }

  printWindow.document.write(html);
  printWindow.document.close();

  // Wait for content to load then trigger print
  return new Promise((resolve) => {
    printWindow.onload = () => {
      // Convert to base64 for saving
      const base64 = btoa(unescape(encodeURIComponent(html)));
      printWindow.close();
      resolve(base64);
    };
  });
}

export async function savePDF(company: CompanyResearch): Promise<string> {
  const html = generatePDFHTML(company);
  const base64 = btoa(unescape(encodeURIComponent(html)));

  const filename = `${company.name.replace(/[^a-zA-Z0-9]/g, '_')}_Valuation_${Date.now()}.html`;

  // Use Electron API to save
  if (window.electronAPI) {
    const filePath = await window.electronAPI.pdf.save(filename, base64);
    return filePath;
  }

  throw new Error('Electron API not available');
}

export function openPDF(filePath: string): void {
  if (window.electronAPI) {
    window.electronAPI.pdf.open(filePath);
  }
}

export function downloadPDFInBrowser(company: CompanyResearch): void {
  const html = generatePDFHTML(company);
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `${company.name.replace(/[^a-zA-Z0-9]/g, '_')}_Valuation.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
