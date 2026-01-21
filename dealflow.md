# EAI DealFlow Terminal (DFT)  
**Version 2.0 // Product Specification & Technical Architecture**  
**Classification:** Internal // proprietary  
**Last Updated:** January 2026  

---

## 1. Executive Vision  
The **EAI DealFlow Terminal (DFT)** is a bespoke, high-frequency acquisition engine designed to replace manual Excel workflows with an AI-augmented "Command Center."  

**The Goal:** Reduce analyst time-to-pitch from **45 minutes** to **<60 seconds** per lead.  
**The Aesthetic:** "High-Finance SaaS." Think **Stripe Dashboard** meets **Bloomberg Terminal**. Dark, fast, precision-engineered.  

---

## 2. Technical Architecture: "The Local Titan"  
To achieve the requirement of **"Insane UI Quality"** (React) combined with **"Heavy Financial Logic"** (Python), we utilize a **Client-Server** architecture running locally on the analyst's machine. This bypasses the sandboxing limits of web/mobile apps while delivering a premium native-app feel.

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

### 2.2 Data Flow (Security & Speed)
1.  **Local Ingestion:** Backend scans `/data/` folder on startup → Merges CSVs in memory.  
2.  **Request:** Frontend sends `GET /search?q=Bobs_HVAC` to Backend.  
3.  **Processing:** Backend filters Pandas DataFrame → Calculates "Deal Heat" → Returns JSON.  
4.  **AI Layer:** Backend constructs prompt (anonymized) → Sends to Gemini API → Returns strategy text.  
5.  **Rendering:** Frontend receives JSON → Renders interactive charts & "Glass" cards.  

**Security Note:**  
*   **API Keys:** Stored in a local `.env` file (e.g., `GEMINI_API_KEY=xyz`). The Backend reads this on boot. The Frontend **never** sees this key.  
*   **Data Privacy:** Raw CSV data **never** leaves the local machine. Only aggregated stats (e.g., "Median Revenue: $5M") are sent to Gemini for context.

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

## 4. Feature Specifications  

### 4.1 The Data Ingestion Engine (Auto-Pilot)  
*   **Behavior:** On startup, the system recursively scans the local `/data/` directory.  
*   **Smart Merge:** Automatically detects CSVs.  
*   **Normalization:**  
    *   *Input:* `SDE Margin`, `SDE %`, `Cash Flow Margin` → *Normalized:* `sde_margin`.  
    *   *Cleaning:* Removes `$`, `,`, `%` automatically. Casts to `float64`.  
*   **Error Handling:** Silently skips corrupt rows, logging a warning to the UI status footer.  

### 4.2 The "Deal Heat" Algorithm (Real-Time Scoring)  
A live confidence score (0-100) displayed in the sidebar.  
*   **Base:** 50 Points.  
*   **Sweet Spot Bonus (+25):** Revenue is \$2M - \$10M.  
*   **Data Confidence (+15):** Peer group has >5 matches.  
*   **Market Health (+10):** Median Peer EBITDA Margin > 15%.  
*   **Visual:** linear-gradient progress bar.  
    *   `< 50`: Red Glow.  
    *   `50-75`: Yellow Glow.  
    *   `> 75`: Green + Cyan Glow.  

### 4.3 The Market Galaxy (Visualization)  
*   **Tech:** Recharts or Nivo (React) or Plotly.js.  
*   **Mode:** Scatter Plot.  
*   **X-Axis:** Revenue ($) Log Scale option.  
*   **Y-Axis:** EBITDA Margin (%).  
*   **Interaction:**  
    *   **The Target:** A large, pulsing cyan orb.  
    *   **Peers:** Small ghost dots. Hovering dims all others and highlights the peer's anonymized stats.  

### 4.4 The AI Strategist (Gemini 2.0)  
*   **Trigger:** User clicks "Analyze Deal."  
*   **Input:** Target Name, Revenue, Website URL.  
*   **Process:**  
    1.  **Scrape:** Fetches public meta-description from URL (conceptually).  
    2.  **Benchmark:** Compares Target vs. Peer Median.  
    3.  **Draft:** Gemini 2.0 Flash generates 3 distinct outreach angles.  
*   **Output Tabs:**  
    1.  **"The Hook":** Pattern matching ("We saw companies like X sold for Y...").  
    2.  **"The Value":** "I prepared a valuation report..."  
    3.  **"The Nudge":** Short, low friction.  

### 4.5 The One-Pager Generator (PDF)  
*   **Action:** Click "Export Report."  
*   **Backend:** Uses `fpdf2` or `reportlab`.  
*   **Content:**  
    *   **Header:** EAI Capital Logo (Gold/White).  
    *   **Dynamic Chart:** Static image of the scatter plot (generated via backend plotting).  
    *   **Valuation Matrix:** Low/Base/High estimate based on peer multiples.  
    *   **Upside:** 3 AI-generated bullet points on operational improvements.  

---

## 5. Development Roadmap (Checklist)  

### Phase 1: The Skeleton (Hours 0-2)  
- [ ] Initialize FastAPI Backend (`poetry init`).  
- [ ] Initialize React Frontend (`npm create vite@latest`).  
- [ ] Implement `DataIngestion` class (CSV scanning).  
- [ ] Verify basic frontend-backend communication (`Hello World` ping).  

### Phase 2: The Logic (Hours 2-5)  
- [ ] Implement Pandas normalization logic.  
- [ ] Build "Peer Group" filtering endpoint.  
- [ ] Implement "Deal Heat" scoring algorithm.  
- [ ] Wire up basic Charts (random data -> real data).  

### Phase 3: The Brain (Hours 5-8)  
- [ ] Create `GeminiService` class.  
- [ ] Engineer "The Hook" prompts.  
- [ ] Build PDF generation route.  

### Phase 4: The Polish (Hours 8+)  
- [ ] Apply "Dark Glass" CSS theme.  
- [ ] Add loading skeletons and spinners.  
- [ ] Refine responsive layouts.  

---

## 6. How to Run (Simple)  
We will provide a single script `start_terminal.sh` that launches both services.  

```bash
# 1. Start Backend (in terminal tab 1)
cd backend && poetry run uvicorn main:app --reload

# 2. Start Frontend (in terminal tab 2)
cd frontend && npm run dev
```

*The Analysts just browse to `localhost:5173` and the terminal is live.*
