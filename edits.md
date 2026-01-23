# Planned Edits & Enhancements

## 1. Design Methodology: 0xDesign Integration
**Goal:** Use the "Design and Refine" iterative process to achieve "Insanely High Quality" UI.
*   **Iterative Variations**: For key screens (History, Main Dashboard), generate distinct variations (layouts, densities) before committing. Compare side-by-side.
*   **Aesthetic**: "Black Glass" / "Liquid Glass" (Professional Grade).
    *   **Refined CSS**:
        ```css
        background: rgba(14, 17, 23, 0.7); /* Slightly more transparent for depth */
        backdrop-filter: blur(24px);      /* Heavier premium blur */
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08); /* Crisp edge */
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05); /* Inner light ring */
        ```
    *   **Backgrounds**: Use subtle Mesh Gradients (deep purple/slate) to ensure the glass effect is visible and premium.
*   **Framework**: Next.js + Tailwind CSS + Framer Motion.

## 2. Interaction & Layout Fixes
*   **Scrolling**:
    *   **CRITICAL FIX**: Full vertical scrolling for Research/Email views. No tiny scrollbars.
*   **Settings UI**:
    *   **Fix**: Stop it from being "glitched at the bottom".
    *   **Requirement**: Use a proper **Slide-Over Panel** or **Centered Modal** that is fully accessible and visually distinct.
*   **History Page**:
    *   **Fix**: Populate with detailed grid data. Remove "boring" empty space.

## 3. Data Accuracy & Integrity
*   **Strict Rule**: **REAL DATA ONLY**.
    *   **Validation**: The AI must cross-reference data.
    *   **Tesla Example**: Ensure "Revenue" and "Margins" match reality. If Gemini returns 2021 data, label it "2021". Do NOT allow hallucinated "current" numbers.
    *   **Visuals**: If data is missing, **hide the graph**. Do not plot random/mock numbers.
    *   **Data Sources**: Use reliable data sources (e.g., SEC filings, company websites, public reports).
    *   **Data Verification**: Cross-reference data with multiple sources to ensure accuracy.
    *   **Data Validation**: Verify data against known facts and industry trends.
    *   **Data Sources**: Use reliable data sources (e.g., SEC filings, company websites, public reports).

## 4. Feature: Email Persistence
*   **Requirement**: Save generated emails automatically.
    *   **Storage**: Store them alongside PDFs in the History.
    *   **UI**: Allow users to "View Saved Drafts" for any past company.

## 5. Hyper-Personalized Email Engine
**Goal:** "Smart Friend Over Coffee" Tone.
*   **Tone**: Forward, technical, no AI fluff.
*   **Targeting**: Address "Company Team" if no person found.
*   **UI Controls**:
    *   **Copy to Clipboard**.
    *   **Expand View**.
*   **Prohibitions**:
    *   **NO EM-DASHES**.
    *   Remove "Re:" from initial subjects.

## 6. "Wall Street Grade" PDF Analysis
**Goal:** Investment Bank Quality.
*   **Density**: Sparklines, SWOT grids, Valuation Bridges.
*   **Aesthetics**: $5,000 consultancy report feel.
