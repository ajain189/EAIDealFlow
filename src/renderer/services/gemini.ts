import { CompanyResearch, GeneratedEmail, EmailTone, EmailType } from '../types';
import { AIProvider } from '../components/SettingsModal';

// API endpoints for each provider
const API_ENDPOINTS = {
  openrouter: 'https://openrouter.ai/api/v1/chat/completions',
  openai: 'https://api.openai.com/v1/chat/completions',
  anthropic: 'https://api.anthropic.com/v1/messages',
  gemini: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
};

// Default models for each provider
const DEFAULT_MODELS = {
  openrouter: 'google/gemini-2.0-flash-001',
  openai: 'gpt-4o',
  anthropic: 'claude-3-5-sonnet-20241022',
  gemini: 'gemini-1.5-flash',
};

// Current configuration
let currentConfig = {
  provider: 'openrouter' as AIProvider,
  apiKey: '',
};

export function setAIConfig(provider: AIProvider, apiKey: string) {
  console.log('setAIConfig called with provider:', provider, 'apiKey length:', apiKey?.length || 0);
  currentConfig = {
    provider: provider || 'openrouter',
    apiKey: apiKey || '',
  };
  console.log('currentConfig updated:', { provider: currentConfig.provider, hasApiKey: !!currentConfig.apiKey });
}

export function getAIConfig() {
  return { ...currentConfig };
}

// Legacy function for backwards compatibility
export function setApiKey(apiKey: string) {
  currentConfig.apiKey = apiKey || '';
}

export function getApiKey(): string {
  return currentConfig.apiKey;
}

// Call OpenRouter API
async function callOpenRouter(prompt: string, apiKey: string): Promise<string> {
  const response = await fetch(API_ENDPOINTS.openrouter, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://dealflow-terminal.app',
      'X-Title': 'DealFlow Terminal',
    },
    body: JSON.stringify({
      model: DEFAULT_MODELS.openrouter,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 4096,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `OpenRouter API error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0]?.message?.content || '';
}

// Call OpenAI API
async function callOpenAI(prompt: string, apiKey: string): Promise<string> {
  const response = await fetch(API_ENDPOINTS.openai, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: DEFAULT_MODELS.openai,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 4096,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `OpenAI API error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0]?.message?.content || '';
}

// Call Anthropic API
async function callAnthropic(prompt: string, apiKey: string): Promise<string> {
  const response = await fetch(API_ENDPOINTS.anthropic, {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: DEFAULT_MODELS.anthropic,
      max_tokens: 4096,
      messages: [{ role: 'user', content: prompt }],
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Anthropic API error: ${response.status}`);
  }

  const data = await response.json();
  return data.content[0]?.text || '';
}

// Call Google Gemini API
async function callGemini(prompt: string, apiKey: string): Promise<string> {
  const url = `${API_ENDPOINTS.gemini}?key=${apiKey}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 4096,
      },
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Gemini API error: ${response.status}`);
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
}

// Unified API call function
async function callAI(prompt: string): Promise<string> {
  const { provider, apiKey } = currentConfig;
  console.log('callAI using provider:', provider, 'apiKey length:', apiKey?.length || 0);

  if (!apiKey) {
    throw new Error('No API key configured. Please add your API key in Settings.');
  }

  // Use IPC to call API from main process (avoids CORS/cookie issues in Electron)
  if (window.electronAPI?.ai?.call) {
    console.log('Using IPC for AI call');
    const result = await window.electronAPI.ai.call({ provider, apiKey, prompt });
    if (!result.success) {
      throw new Error(result.error || 'AI API call failed');
    }
    return result.data;
  }

  // Fallback to direct fetch (for browser/dev mode)
  console.log('Using direct fetch for AI call');
  switch (provider) {
    case 'openai':
      return callOpenAI(prompt, apiKey);
    case 'anthropic':
      return callAnthropic(prompt, apiKey);
    case 'gemini':
      return callGemini(prompt, apiKey);
    case 'openrouter':
    default:
      return callOpenRouter(prompt, apiKey);
  }
}

export async function researchCompany(
  companyName: string,
  websiteUrl: string
): Promise<CompanyResearch> {
  const prompt = `You are a business analyst researching a company for an investment firm.

Analyze the company "${companyName}" using their website: ${websiteUrl}

Research this company thoroughly and extract the following information. Be factual and professional.

Return your findings as a valid JSON object with this exact structure:
{
  "name": "The official company name",
  "description": "A 2-3 sentence professional overview of what the company does",
  "services": ["Service or product 1", "Service or product 2", "Service or product 3"],
  "industry": "Primary industry category (e.g., HVAC, Transportation, Manufacturing, Technology)",
  "keyMetrics": ["Notable achievement or metric if found", "Another metric or leave empty array if none"],
  "competitiveAdvantage": "One sentence about what makes them unique or their market position",
  "ownershipHints": "Any ownership, leadership, or founding information found, or 'Not publicly available'",
  "yearFounded": "Year if found, or 'Unknown'",
  "location": "City, State if found, or 'Unknown'",
  "employeeCount": "Approximate employee count if found, or 'Unknown'"
}

Important:
- Be factual, do not invent information
- If information is not available, use appropriate placeholders
- Keep descriptions professional and concise
- Return ONLY valid JSON, no markdown code blocks or additional text`;

  try {
    console.log('Starting AI API call for:', companyName);
    const text = await callAI(prompt);
    console.log('AI response received:', text.substring(0, 200));

    // Clean the response - remove markdown code blocks if present
    let cleaned = text.trim();
    if (cleaned.startsWith('```json')) {
      cleaned = cleaned.slice(7);
    } else if (cleaned.startsWith('```')) {
      cleaned = cleaned.slice(3);
    }
    if (cleaned.endsWith('```')) {
      cleaned = cleaned.slice(0, -3);
    }
    cleaned = cleaned.trim();

    const parsed = JSON.parse(cleaned);
    console.log('Successfully parsed company data');
    return parsed;
  } catch (error: any) {
    console.error('Error researching company:', error);
    const errorMsg = error?.message || error?.toString() || 'Unknown error';
    console.error('Full error:', errorMsg);

    if (errorMsg.includes('API key') || errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
      throw new Error('Invalid API key. Please check your API key in Settings.');
    } else if (errorMsg.includes('quota') || errorMsg.includes('429') || errorMsg.includes('rate')) {
      throw new Error('API rate limit reached. Please wait a moment and try again.');
    } else if (errorMsg.includes('JSON') || errorMsg.includes('parse')) {
      throw new Error('Failed to parse AI response. Please try again.');
    } else if (errorMsg.includes('fetch') || errorMsg.includes('network') || errorMsg.includes('Failed to fetch')) {
      throw new Error('Network error. Please check your internet connection.');
    }

    throw new Error(`Research failed: ${errorMsg}`);
  }
}

const TONE_INSTRUCTIONS: Record<EmailTone, string> = {
  formal: 'Write in a formal, professional tone. Address the team as "Hi [Company Name] Team" (e.g., "Hi Acme Team"). NEVER invent a specific person name like "CEO" or "Manager" unless we have actual names from research. Be respectful and business-appropriate. End with a proper sign-off like "Best regards," or "Sincerely," followed by a line break and then the name placeholder "[Your Name]".',
  friendly: 'Write in a warm, personable but professional tone. Address as "Hi [Company Name] Team". Be conversational while maintaining professionalism. Feel like a smart peer reaching out, not a salesperson. Sound like a smart friend having coffee, technical and forward. End with a casual but complete sign-off like "Best," or "Talk soon," followed by a line break and "[Your Name]".',
  direct: 'Write in a concise, forward, action-oriented tone. No fluff, no pleasantries. Address as "Hi [Company Name] Team". Get straight to the point in 2-3 sentences max. Technical and confident. End with a brief sign-off like "Regards," followed by "[Your Name]".',
};

// Post-process email to remove any em-dashes and ensure clean formatting
function cleanEmailContent(email: GeneratedEmail): GeneratedEmail {
  const cleanText = (text: string): string => {
    return text
      // Remove em-dashes and en-dashes, replace with commas or hyphens
      .replace(/\u2014/g, ', ')  // em-dash
      .replace(/\u2013/g, '-')   // en-dash
      .replace(/—/g, ', ')
      .replace(/–/g, '-')
      // Remove "Re:" prefix from initial outreach subjects
      .replace(/^Re:\s*/i, '')
      // Clean up any double spaces
      .replace(/\s{2,}/g, ' ')
      .trim();
  };

  return {
    subject: cleanText(email.subject),
    body: cleanText(email.body),
  };
}

// Build hyper-specific email prompts that reference actual company data
const EMAIL_TYPE_PROMPTS: Record<EmailType, (company: CompanyResearch) => string> = {
  hook: (company) => {
    const specificService = company.services[0] || 'core offerings';
    const competitiveNote = company.competitiveAdvantage || '';
    const locationNote = company.location && company.location !== 'Unknown' ? ` based in ${company.location}` : '';
    const foundedNote = company.yearFounded && company.yearFounded !== 'Unknown' ? ` (est. ${company.yearFounded})` : '';
    const ownerNote = company.ownershipHints && company.ownershipHints !== 'Not publicly available' ? company.ownershipHints : '';

    return `Write an initial outreach email to ${company.name}${locationNote}${foundedNote}, a company in the ${company.industry} sector.

CRITICAL - You MUST reference these SPECIFIC details from our research:
1. Their primary service: "${specificService}" - mention this SPECIFICALLY, not generically
2. Their competitive position: "${competitiveNote}" - weave this naturally into why we're reaching out
${ownerNote ? `3. Leadership context: "${ownerNote}" - if there's a founder/owner name, address them directly` : ''}
${company.keyMetrics.length > 0 && company.keyMetrics[0] ? `4. Notable metric: "${company.keyMetrics[0]}" - reference this achievement` : ''}

The email MUST:
- Open with a specific observation about their business (NOT generic "I came across your company")
- Reference at least ONE specific service/product they offer by name
- Connect their competitive strength to why a private equity conversation makes sense NOW
- Be 3-4 sentences max in the body
- Feel like it could ONLY be sent to THIS company - if you could swap in another company name without changing anything else, you've FAILED

Example of BAD (too generic): "I noticed your company provides great services in the HVAC industry..."
Example of GOOD (specific): "Your focus on commercial refrigeration retrofits caught my attention - the energy efficiency angle positions you well in today's market..."`;
  },

  asset: (company) => {
    const industryBenchmark = company.industry || 'your sector';
    const specificMetric = company.keyMetrics[0] || '';

    return `Write a follow-up email to ${company.name} offering a complimentary valuation analysis.

Context from our research:
- Industry: ${company.industry}
- Their positioning: "${company.competitiveAdvantage}"
${specificMetric ? `- Notable metric: "${specificMetric}"` : ''}

The email MUST:
- Reference our previous outreach naturally (not "Following up on my last email...")
- Offer a complimentary one-page valuation snapshot as a genuine value-add
- Mention that we've benchmarked against ${industryBenchmark} transactions from the past 18 months
- Note the PDF analysis is attached
- Be 2-3 sentences max
- Make it clear this is about providing insight, not pushing a transaction

Frame the valuation as: "Given ${company.name}'s position in ${specificMetric ? `achieving ${specificMetric}` : 'the market'}, I thought you might find this useful regardless of any near-term plans."`;
  },

  close: (company) => {
    return `Write a brief final follow-up email to ${company.name}.

Context:
- We previously sent them a valuation analysis
- Industry: ${company.industry}
- Their strength: "${company.competitiveAdvantage}"

The email MUST:
- Be exactly 2 sentences in the body, no more
- Reference the valuation report we sent
- Acknowledge they're busy (respect for their time)
- Make the ask small and specific: "5 minutes" or "quick call this week"
- NOT be pushy or use urgency tactics
- Feel like a genuine, low-pressure check-in

The tone should be: "I know you're busy, but if this landed at a relevant time, I'm around."`;
  },
};

export async function generateEmail(
  company: CompanyResearch,
  tone: EmailTone,
  type: EmailType
): Promise<GeneratedEmail> {
  const prompt = `You are a senior business development professional at EAI Capital, a private equity firm focused on lower middle market investments in industrial and commercial services businesses.

${EMAIL_TYPE_PROMPTS[type](company)}

Tone: ${TONE_INSTRUCTIONS[tone]}

Return ONLY a valid JSON object:
{
  "subject": "The email subject line - make it specific to ${company.name}, NOT generic",
  "body": "The email body text"
}

STRICT REQUIREMENTS:
1. ZERO emojis anywhere in subject or body
2. ABSOLUTELY NO EM-DASHES (the long dash character). Use commas, periods, or rewrite sentences instead
3. NO generic phrases like "hope this finds you well", "I wanted to reach out", "touching base"
4. NO AI-sounding language like "leverage", "synergies", "unlock value", "strategic partnership"
5. The subject line must be specific enough that ${company.name} would recognize it's about THEM
6. For INITIAL outreach (hook email): NEVER use "Re:" prefix - this is a FIRST email, not a reply
7. For follow-up emails (asset, close): Using "Re:" is acceptable since we're continuing a thread
8. Address the COMPANY TEAM (e.g., "Hi ${company.name} Team") - NEVER invent a person's name or title
9. Sound like a human who actually read about this company, not a mail merge
10. ALWAYS include a proper sign-off and signature at the end: e.g., "Best regards,\\n\\n[Your Name]"

BAD subject: "Re: Partnership Opportunity" (fake reply, generic)
BAD subject: "Quick question for the CEO" (inventing titles)
GOOD subject: "${company.name}'s ${company.industry} growth trajectory"
GOOD subject: "Question about ${company.name}'s expansion"

Return ONLY the JSON, no markdown blocks or explanation.`;

  try {
    const text = await callAI(prompt);

    // Clean the response
    let cleaned = text.trim();
    if (cleaned.startsWith('```json')) {
      cleaned = cleaned.slice(7);
    } else if (cleaned.startsWith('```')) {
      cleaned = cleaned.slice(3);
    }
    if (cleaned.endsWith('```')) {
      cleaned = cleaned.slice(0, -3);
    }
    cleaned = cleaned.trim();

    const parsedEmail = JSON.parse(cleaned);

    // Post-process to ensure no em-dashes and clean formatting
    return cleanEmailContent(parsedEmail);
  } catch (error: any) {
    console.error('Error generating email:', error);
    throw new Error('Failed to generate email. Please try again.');
  }
}

export async function generateAllEmails(
  company: CompanyResearch,
  tone: EmailTone
): Promise<Record<EmailType, GeneratedEmail>> {
  const [hook, asset, close] = await Promise.all([
    generateEmail(company, tone, 'hook'),
    generateEmail(company, tone, 'asset'),
    generateEmail(company, tone, 'close'),
  ]);

  return { hook, asset, close };
}
