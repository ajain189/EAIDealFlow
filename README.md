# EAI DealFlow

A desktop application built for EAI Capital to streamline the company research and outreach process for investment analysts. This project was developed as a functional mockup to demonstrate how AI can be integrated into the private equity deal sourcing workflow.

## What It Does

EAI DealFlow takes a company name and website URL, then uses AI to automatically:

1. Research the company and pull key information (services, industry, location, competitive advantages, etc.)
2. Generate a PDF report summarizing the findings
3. Create personalized outreach emails tailored to that specific company

The goal is to save analysts hours of manual research by automating the initial discovery phase of deal sourcing.

## Features

**Company Research**
- Enter any company name and website
- AI analyzes the company and extracts relevant business information
- Results include industry classification, services offered, competitive positioning, and ownership hints

**PDF Reports**
- Automatically generates a clean, professional PDF report for each company
- Reports can be opened directly or downloaded for sharing

**Email Generation**
- Creates three types of outreach emails: initial hook, value-add follow-up, and soft close
- Choose between formal, friendly, or direct tones
- Emails reference specific details about the company (not generic templates)

**Multiple AI Providers**
- Works with OpenRouter, OpenAI, Anthropic (Claude), or Google Gemini
- Bring your own API key through the settings menu

**History**
- Saves all researched companies locally
- Quickly revisit past research and generated emails

## Installation

Download the latest release for your operating system:

- **macOS**: Download the `.dmg` file, open it, and drag the app to your Applications folder
- **Windows**: Download the `.exe` installer and run it

[Download from Releases](https://github.com/ajain189/EAIDealFlow/releases)

## Setup

1. Open the app
2. Click on Settings in the sidebar
3. Select your AI provider and paste your API key
4. Start researching companies

## Tech Stack

- Electron (desktop framework)
- React + TypeScript (frontend)
- Vite (build tool)
- Framer Motion (animations)

## Development

To run locally:

```bash
git clone https://github.com/ajain189/EAIDealFlow.git
cd EAIDealFlow
npm install
npm run dev
```

To build for distribution:

```bash
npm run package:mac    # macOS
npm run package:win    # Windows
npm run package:linux  # Linux
```

## About

This project was commissioned by EAI Capital as a proof-of-concept tool for their investment analyst team. It demonstrates how AI-assisted research can fit into the lower middle market private equity workflow, specifically for sourcing and initial outreach to potential acquisition targets in the industrial and commercial services sectors.

## License

MIT
