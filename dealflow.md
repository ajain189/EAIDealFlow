# DealFlow Terminal

AI-powered company research and outreach generator for investment analysts.

---

## Overview

DealFlow Terminal is a desktop application that helps investment analysts research companies and generate personalized outreach. Enter a company name and website URL, and the app uses Google Gemini to research the company, generate a professional PDF report, and create customizable email templates.

**Core Flow:**
1. Enter company name and website URL
2. Gemini AI researches and analyzes the company
3. View research results and download PDF report
4. Generate personalized emails in different tones
5. All reports saved locally with full history

---

## Quick Start

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Package as desktop app
npm run package:mac   # Creates .dmg for macOS
npm run package:win   # Creates .exe for Windows
npm run package:linux # Creates .AppImage for Linux
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Electron 28 |
| Frontend | React 18 + TypeScript |
| Build Tool | Vite 5 |
| AI | Google Gemini 2.0 Flash |
| Storage | electron-store (local JSON) |
| PDF | HTML-to-PDF generation |
| Packaging | electron-builder |

---

## Project Structure

```
DealFlow/
├── src/
│   ├── main/                    # Electron main process
│   │   ├── main.ts              # App entry, window management, IPC
│   │   └── preload.ts           # Bridge between main and renderer
│   └── renderer/                # React frontend
│       ├── components/
│       │   ├── ui/              # Core UI components
│       │   │   ├── GlassCard.tsx
│       │   │   ├── Button.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Tabs.tsx
│       │   │   ├── Badge.tsx
│       │   │   └── LoadingState.tsx
│       │   ├── Layout.tsx       # App shell and navigation
│       │   ├── CompanyInput.tsx # Research form
│       │   ├── ReportPreview.tsx# Research results display
│       │   ├── EmailGenerator.tsx# Email generation UI
│       │   └── HistoryList.tsx  # Saved reports list
│       ├── services/
│       │   ├── gemini.ts        # Gemini API integration
│       │   ├── pdf.ts           # PDF generation
│       │   └── storage.ts       # Local history management
│       ├── styles/
│       │   ├── theme.ts         # Design tokens
│       │   └── global.css       # Base styles
│       ├── types/
│       │   └── index.ts         # TypeScript interfaces
│       ├── App.tsx              # Main application component
│       ├── main.tsx             # React entry point
│       └── index.html           # HTML template
├── assets/                      # App icons
├── package.json
├── tsconfig.json
├── tsconfig.main.json
├── vite.config.ts
└── electron-builder.yml
```

---

## Design System

### Theme: Dark Glass

Premium, sophisticated aesthetic inspired by Stripe and Linear.

### Colors

```typescript
const colors = {
  // Backgrounds
  background: '#0E1117',
  backgroundLight: '#161B22',

  // Glass panels
  glass: 'rgba(255, 255, 255, 0.03)',
  glassBorder: 'rgba(255, 255, 255, 0.08)',

  // Primary (Blurple gradient)
  primary: '#6366f1',
  secondary: '#8b5cf6',

  // Accents
  cyan: '#06b6d4',
  emerald: '#10b981',
  amber: '#f59e0b',
  red: '#ef4444',

  // Text
  textPrimary: '#ffffff',
  textSecondary: '#9ca3af',
  textMuted: '#6b7280',
};
```

### Typography

- **UI Text:** Inter, -apple-system, sans-serif
- **Monospace:** JetBrains Mono (for data)
- **Sizes:** 11px (xs) to 36px (4xl)

### Spacing

```typescript
const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px',
};
```

### Border Radius

```typescript
const borderRadius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
};
```

---

## Features

### Company Research

The app uses Gemini AI to analyze a company's website and extract:

- Company name and description
- Core services/products
- Industry classification
- Key metrics and achievements
- Competitive advantages
- Ownership information
- Location and founding year

### PDF Reports

Generated reports include:

- EAI Capital branding
- Company overview
- Services grid
- Competitive position highlight
- Key metrics
- Professional formatting

### Email Generator

Three email types with three tone options:

**Email Types:**
1. **Hook** - Initial outreach, introduces opportunity
2. **Asset** - Follow-up with valuation snapshot offer
3. **Close** - Brief final nudge for a call

**Tone Options:**
- **Formal** - Professional, respectful, "Dear" greeting
- **Friendly** - Warm, personable, "Hi" greeting
- **Direct** - Concise, action-oriented, "Hello" greeting

### History Management

- All reports saved locally
- Quick access in sidebar
- Full history view
- Delete individual or bulk entries
- Persistent across sessions

---

## API Integration

### Gemini Configuration

The app uses Google Gemini 2.0 Flash for all AI operations:

```typescript
const API_KEY = 'AIzaSyCprbttLpBkPX0EeQU56BbRpG4x7flRpSc';
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
```

### Research Prompt

The research prompt extracts structured company data:

```typescript
const prompt = `Analyze the company "${companyName}" using their website: ${websiteUrl}

Return a JSON object with:
- name, description, services, industry
- keyMetrics, competitiveAdvantage
- ownershipHints, yearFounded, location, employeeCount`;
```

### Email Prompts

Each email type has specific instructions:

- **Hook:** Reference services, mention opportunity
- **Asset:** Offer valuation snapshot, mention PDF
- **Close:** Brief nudge for 5-minute call

---

## Local Storage

### Data Location

- **macOS:** `~/Library/Application Support/dealflow-terminal/`
- **Windows:** `%APPDATA%/dealflow-terminal/`
- **Linux:** `~/.config/dealflow-terminal/`

### Storage Format

```typescript
interface HistoryEntry {
  id: string;
  companyName: string;
  websiteUrl: string;
  research: CompanyResearch;
  emails: Record<string, GeneratedEmail>;
  pdfPath: string | null;
  createdAt: string;
}
```

---

## Building for Distribution

### macOS (.dmg)

```bash
npm run package:mac
```

Output: `release/DealFlow Terminal-2.0.0.dmg`

### Windows (.exe)

```bash
npm run package:win
```

Output: `release/DealFlow Terminal Setup 2.0.0.exe`

### Linux (.AppImage)

```bash
npm run package:linux
```

Output: `release/DealFlow Terminal-2.0.0.AppImage`

---

## User Flow

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Enter Company   | --> |  Gemini Research | --> |  View Results    |
|  Name + Website  |     |  (AI Analysis)   |     |  + Download PDF  |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Access History  | <-- |  Save to History | <-- |  Generate Emails |
|  (Sidebar)       |     |  (Automatic)     |     |  (3 Types/Tones) |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

---

## UI Components

### GlassCard

Container with glassmorphism effect:

```tsx
<GlassCard padding="lg" hover>
  {children}
</GlassCard>
```

### Button

Primary action button with gradient:

```tsx
<Button
  variant="primary"  // primary | secondary | ghost | danger
  size="md"          // sm | md | lg
  loading={false}
  fullWidth
>
  Generate Report
</Button>
```

### Input

Styled text input:

```tsx
<Input
  label="Company Name"
  placeholder="e.g., Acme Corp"
  value={value}
  onChange={setValue}
  error={errorMessage}
/>
```

### Tabs

Tab navigation:

```tsx
<Tabs
  tabs={[
    { id: 'hook', label: '1. Hook' },
    { id: 'asset', label: '2. Asset' },
    { id: 'close', label: '3. Close' },
  ]}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

### Badge

Status indicators:

```tsx
<Badge variant="primary">Technology</Badge>
<Badge variant="success">Active</Badge>
```

---

## Security

- API key stored in app bundle (not exposed to users)
- All data stored locally on user's machine
- No external data transmission except Gemini API calls
- Gemini only receives company name and URL (no proprietary data)

---

## Development

### Running Locally

```bash
# Terminal 1: Start Vite dev server
npm run dev:renderer

# Terminal 2: Start Electron (after Vite is ready)
npm run dev:main

# Or run both together
npm run dev
```

### Building

```bash
# Build for production
npm run build

# Package for distribution
npm run package
```

### File Structure Notes

- `src/main/` - Node.js environment (Electron main process)
- `src/renderer/` - Browser environment (React app)
- Communication via IPC (Inter-Process Communication)

---

## Customization

### Changing API Key

Update the API key in `src/renderer/services/gemini.ts`:

```typescript
const API_KEY = 'your-new-api-key';
```

### Modifying Theme

Edit `src/renderer/styles/theme.ts` to change colors, typography, spacing.

### Adding Email Types

Add new email types in `src/renderer/services/gemini.ts`:

```typescript
const EMAIL_TYPE_PROMPTS = {
  hook: (company) => `...`,
  asset: (company) => `...`,
  close: (company) => `...`,
  // Add new type here
  newType: (company) => `Your prompt...`,
};
```

---

## Troubleshooting

### App won't start

1. Ensure Node.js 18+ is installed
2. Run `npm install` to install dependencies
3. Check that port 5173 is available

### Gemini errors

1. Verify API key is valid
2. Check internet connection
3. Ensure website URL is accessible

### PDF not generating

1. Check console for errors
2. Verify company research completed successfully
3. Try downloading manually with the Download button

---

## Version History

- **v2.0.0** - Complete rewrite with Electron, new UI, local storage
- **v1.0.0** - Initial Streamlit version

---

Built for EAI Capital
