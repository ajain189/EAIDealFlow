# EAI DealFlow Terminal (DFT)  
**Version 2.0 // Product Specification & Technical Architecture**  
**Classification:** Internal // proprietary  
**Last Updated:** January 2026  

---

## 1. Executive Vision  
The **EAI DealFlow Terminal (DFT)** is a bespoke, AI-powered sourcing engine designed to replace manual Excel workflows with an AI-augmented "Command Center."  

**The Goal:** Reduce analyst time-to-pitch from **45 minutes** to **<60 seconds** per lead.  
**The Aesthetic:** "High-Finance SaaS." Think **Stripe Dashboard** meets **Bloomberg Terminal**. Dark, fast, precision-engineered.  

**Core Workflow:**  
1.  **Manual Entry:** Analyst inputs a target's raw details (Name, URL, Revenue).  
2.  **Auto-Context:** System scrapes the website & AI infers operational details.  
3.  **Auto-Benchmark:** System compares the target against EAI's proprietary CSV database.  
4.  **Output:** Generates a "Killer" One-Pager PDF + Hyper-personalized Drip Campaign.

---

## 2. Technical Architecture: "The Local Titan"  
To achieve the requirement of **"Insane UI Quality"** (React) combined with **"Heavy Financial Logic"** (Python), we utilize a **Hybrid Client-Server** architecture running locally on the analyst's machine. This bypasses the sandboxing limits of web/mobile apps while delivering a premium native-app feel.

### 2.1 The Stack  
| Layer | Technology | Reason for Choice |
| :--- | :--- | :--- |
| **Frontend** | **React (Vite) + TypeScript** | Enables pixel-perfect "Glassmorphism" UI, complex animations, and instant interactivity that Streamlit/Expo cannot match. |
| **Styling** | **Tailwind CSS** | Rapid styling for the sophisticated "Dark Mode" aesthetic. |
| **Motion** | **Framer Motion** | For "sleek," "expensive-feeling" micro-interactions (hover glows, smooth transitions). |
| **Backend** | **Python 3.12 + FastAPI** | The industry standard for high-performance Python APIs. Handles all file I/O and Math. |
| **Data Engine** | **Pandas + NumPy** | Deterministic financial math and CSV normalization. |
| **AI Core** | **Google Gemini 2.0 Flash** | Selected for low-latency reasoning and high-context windows. |
| **Storage** | **Local Filesystem** | Zero-latency, secure, privacy-first data handling. No external DB required. |

---

## 3. Design System: "Obsidian & Glass"  
The UI must feel like a tool for elite professionals. It should startle the user with its quality.

*   **Background:** Deepest Charcoal (`#0E1117`) with a subtle radial gradient top-center (`#1a1f2e` to transparent) to create a "spotlight" effect.
*   **Surfaces (The Glass):**  
    *   `bg-white/5` (5% opacity white)  
    *   `backdrop-blur-md` (12px blur)  
    *   `border border-white/10` (Subtle 1px rim)  
*   **Primary Accent:** **Electric Blurple** (`#6366f1` to `#8b5cf6` gradient). Used *only* for primary actions like "Generate Strategy."
*   **Data Colors:**  
    *   **Target (You):** Cyan (`#06b6d4`) - Pulsing effect.  
    *   **Market (Peers):** Ghost White (`#9ca3af`) - 40% Opacity.  
    *   **Success:** Emerald (`#10b981`).  
    *   **Warning:** Amber (`#f59e0b`).  
*   **Typography:** `Inter` (UI) and `JetBrains Mono` (Financials).  

---

## 4. Functional Requirements  

### 4.1 The Reference Database (The "Brain")  
The CSV files in the `/data/` directory act as the "Intelligence Bank." **They are not the leads list.** They are the *benchmark*.  
*   **Auto-Ingest:** On startup, the system absorbs all CSVs (e.g., `HVAC_Sales_2024.csv`, `SaaS_Multiples.csv`).  
*   **Normalization:** It unifies columns (`SDE`, `EBITDA`, `Revenue`) into a single "Market Truth" dataframe.  
*   **Purpose:** When you type in a new target ("Bob's Plumbing"), the system looks at this database to say: *"Compared to 500 other plumbers, Bob is undervalued."*  

### 4.2 The "Deal Heat" Algorithm (Real-Time Scoring)  
A live confidence score (0-100) displayed in the sidebar *as you type* the manual listing.  
*   **Inputs:** Revenue Input, Industry Selection, Scraped Data Quality.  
*   **Logic:**  
    *   **Base:** 50 Points.  
    *   **Sweet Spot Bonus (+25):** If Revenue is \$2M - \$10M (EAI's buy box).  
    *   **Market Confidence (+15):** If we have >5 peer comps in the CSV database.  
    *   **Margin Health (+10):** If the *projected* margin > Independent Peer Median.  
*   **Visual:** A glowing progress bar that changes color (Red -> Yellow -> Green) as the deal looks better.  

### 4.3 The Market Galaxy (Visualization)  
*   **Tech:** Recharts / Plotly.js (React).  
*   **Mode:** Scatter Plot.  
*   **X-Axis:** Revenue ($).  
*   **Y-Axis:** EBITDA Margin (%).  
*   **Visual Strategy:**  
    *   **Ghost Dots (White/Grey):** These are the rows from your **CSV files** (the peers).  
    *   **Pulsing Orb (Cyan):** This is the **Manual Input** (the target).  
    *   **The Story:** The chart visually demonstrates the "Arbitrage Gap" between the target and the market.  

---

## 5. The Content Engine (AI + PDF)  

### 5.1 The AI Context Scraper (Gemini)  
*   **Input:** Analyst provides `www.target-url.com`.  
*   **Process:**  
    1.  Backend creates a simplified request to Gemini: *"Extract the company operational summary, employee count (if available), and value prop from this text."*  
    2.  **Synthesis:** Combines [Manual Revenue Input] + [Scraped Operational Data] + [CSV Benchmark Data].  

### 5.2 The "One-Pager" Generator (PDF)  
*   **User Action:** Click "Generate Investment Memo."  
*   **Template:** A high-end, designer-quality layout (handled via Python `fpdf2` coord-based drawing).  
*   **Dynamic Validated Content:**  
    1.  **Header:** Target Company Name + EAI Branding.  
    2.  **The "Golden Graph":** Embedding a generated PNG of the Market Scatter Plot.  
    3.  **Valration Matrix:** "Based on our database of {N} similar deals, your valuation range is \$X - \$Y."  
    4.  **Operational Upside:** 3 customized bullet points generated by Gemini based on the gap between *Scraped Ops* and *Benchmark Performance*.  
*   **Why:** This isn't just a generic PDF. It's a "Proof of Work" document that proves to the seller we understand their business.  

---

## 6. User Flow (The "Happy Path")  

1.  **Launch:** Analyst opens the app. The "Reference Database" (CSVs) loads silently in the background (0.5s).  
2.  **Input:** Analyst manually types:  
    *   **Name:** "Bob's HVAC"  
    *   **Website:** "bobshvac.com"  
    *   **Revenue:** "$4.5M"  
    *   **Industry:** Selects "HVAC" from dropdown.  
3.  **Instant Analysis (The "Wow" Moment):**  
    *   The "Deal Heat" bar shoots up to **85/100**.  
    *   The Main Graph renders 50 grey dots (peers) and places "Bob's HVAC" (Cyan Orb) in the "High Revenue / Low Efficiency" quadrant.  
4.  **Strategy:**  
    *   Analyst sees the opportunity: "They are under-monetized compared to peers."  
    *   AI drafts 3 emails referencing this specific data.  
5.  **Artifact:**  
    *   Analyst clicks "Export PDF."  
    *   System generates `Bobs_HVAC_Valuation_EAI.pdf` containing the chart and the valuation logic.  
    *   Analyst attaches to email. Sent.  

---

## 7. Development Roadmap (Checklist)  

### Phase 1: The Skeleton (Hours 0-2)  
- [ ] Initialize FastAPI Backend (`poetry init`).  
- [ ] Initialize React Frontend (`npm create vite@latest`).  
- [ ] Implement `DataIngestion` class (CSV Reference Storage).  
- [ ] Verify basic frontend-backend communication.  

### Phase 2: The Logic (Hours 2-5)  
- [ ] Build the Manual Input Forms (React Hook Form).  
- [ ] Implement "Peer Search" logic (filtering CSVs by User Input).  
- [ ] Wire up the Scatter Plot (React <-> Python JSON).  

### Phase 3: The Brain (Hours 5-8)  
- [ ] Create `GeminiService` class (Scraping + Strategy).  
- [ ] Engineer the "One-Pager" PDF Template (drawing logic).  

### Phase 4: The Polish (Hours 8+)  
- [ ] Apply "Dark Glass" CSS theme.  
- [ ] Add loading skeletons and spinners.  
- [ ] Package with PyInstaller.  

---

## 8. Distribution & Delivery  
*   **Packaging:** PyInstaller builds a single `.exe/.dmg`.  
*   **Distribution:** Send the zip file.  
*   **Reference Data:** The `data/` folder is included in the zip. The user can add their own CSVs to this folder to make the "Brain" smarter over time, but the app works out of the box with provided defaults.
