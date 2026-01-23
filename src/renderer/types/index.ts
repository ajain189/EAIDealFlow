export interface CompanyResearch {
  name: string;
  description: string;
  services: string[];
  industry: string;
  keyMetrics: string[];
  competitiveAdvantage: string;
  ownershipHints: string;
  yearFounded?: string;
  location?: string;
  employeeCount?: string;
}

export interface GeneratedEmail {
  subject: string;
  body: string;
}

export type EmailTone = 'formal' | 'friendly' | 'direct';
export type EmailType = 'hook' | 'asset' | 'close';

export interface HistoryEntry {
  id: string;
  companyName: string;
  websiteUrl: string;
  research: CompanyResearch;
  emails: Record<string, GeneratedEmail>;
  pdfPath: string | null;
  createdAt: string;
}

export interface AppSettings {
  apiKey: string;
}

declare global {
  interface Window {
    electronAPI: {
      store: {
        get: (key: string) => Promise<any>;
        set: (key: string, value: any) => Promise<boolean>;
        delete: (key: string) => Promise<boolean>;
      };
      app: {
        getDataPath: () => Promise<string>;
      };
      pdf: {
        save: (filename: string, data: string) => Promise<string>;
        read: (filePath: string) => Promise<string | null>;
        open: (filePath: string) => Promise<boolean>;
        delete: (filePath: string) => Promise<boolean>;
      };
      ai: {
        call: (config: { provider: string; apiKey: string; prompt: string }) => Promise<{ success: boolean; data?: string; error?: string }>;
      };
    };
  }
}
