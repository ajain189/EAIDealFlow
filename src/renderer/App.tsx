import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Layout, Sidebar, Header, Content, NavItem } from './components/Layout';
import { CompanyInput } from './components/CompanyInput';
import { ReportPreview } from './components/ReportPreview';
import { EmailGenerator } from './components/EmailGenerator';
import { HistoryList } from './components/HistoryList';
import { MarketPositionChart } from './components/MarketPositionChart';
import { SettingsModal, UserSettings } from './components/SettingsModal';
import { GlassCard, ResearchSkeleton } from './components/ui';
import { researchCompany, setAIConfig } from './services/gemini';
import { savePDF, downloadPDFInBrowser, openPDF } from './services/pdf';
import { getHistory, saveToHistory, deleteFromHistory } from './services/storage';
import { CompanyResearch, HistoryEntry, GeneratedEmail } from './types';
import { colors, typography, spacing, borderRadius } from './styles/theme';

type View = 'research' | 'history';

const DEFAULT_SETTINGS: UserSettings = {
  userName: '',
  defaultTone: 'formal',
  companyName: 'EAI Capital',
  aiProvider: 'openrouter',
  apiKey: '',
};

export const App: React.FC = () => {
  const [view, setView] = useState<View>('research');
  const [companyName, setCompanyName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [research, setResearch] = useState<CompanyResearch | null>(null);
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [emails, setEmails] = useState<Record<string, GeneratedEmail>>({});
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<UserSettings>(DEFAULT_SETTINGS);

  // Load history and settings on mount
  useEffect(() => {
    loadHistory();
    loadSettings();
  }, []);

  const loadHistory = async () => {
    const entries = await getHistory();
    setHistory(entries);
  };

  const loadSettings = async () => {
    if (window.electronAPI) {
      const saved = await window.electronAPI.store.get('userSettings');
      if (saved) {
        setSettings(saved);
        // Set the AI provider and API key if saved
        setAIConfig(saved.aiProvider || 'openrouter', saved.apiKey || '');
      }
    }
  };

  const saveSettings = async (newSettings: UserSettings) => {
    setSettings(newSettings);
    // Update the AI provider and API key in the gemini service
    setAIConfig(newSettings.aiProvider || 'openrouter', newSettings.apiKey || '');
    if (window.electronAPI) {
      await window.electronAPI.store.set('userSettings', newSettings);
    }
  };

  const handleResearch = async () => {
    if (!companyName.trim() || !websiteUrl.trim()) {
      setError('Please enter both company name and website URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResearch(null);
    setPdfPath(null);
    setEmails({});

    try {
      const companyData = await researchCompany(companyName, websiteUrl);
      setResearch(companyData);

      let savedPdfPath: string | null = null;
      try {
        if (window.electronAPI) {
          savedPdfPath = await savePDF(companyData);
          setPdfPath(savedPdfPath);
        }
      } catch (pdfError) {
        console.error('PDF save failed:', pdfError);
      }

      await saveToHistory(companyName, websiteUrl, companyData, {}, savedPdfPath);
      await loadHistory();
    } catch (err: any) {
      setError(err.message || 'Failed to research company. Please try again.');
      console.error('Research error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (research) {
      downloadPDFInBrowser(research);
    }
  };

  const handleOpenPDF = () => {
    if (pdfPath) {
      openPDF(pdfPath);
    }
  };

  const handleSelectEntry = (entry: HistoryEntry) => {
    setSelectedEntry(entry);
    setResearch(entry.research);
    setCompanyName(entry.companyName);
    setWebsiteUrl(entry.websiteUrl);
    setPdfPath(entry.pdfPath);
    setEmails(entry.emails || {});
    setView('research');
  };

  const handleDeleteEntry = async (id: string) => {
    await deleteFromHistory(id);
    await loadHistory();
    if (selectedEntry?.id === id) {
      setSelectedEntry(null);
      setResearch(null);
      setCompanyName('');
      setWebsiteUrl('');
      setPdfPath(null);
      setEmails({});
    }
  };

  const handleNewResearch = () => {
    setSelectedEntry(null);
    setResearch(null);
    setCompanyName('');
    setWebsiteUrl('');
    setPdfPath(null);
    setEmails({});
    setError(null);
  };

  const handleEmailsUpdate = async (newEmails: Record<string, GeneratedEmail>) => {
    setEmails(newEmails);
    if (selectedEntry) {
      // Update local state
      const updatedHistory = history.map(h =>
        h.id === selectedEntry.id ? { ...h, emails: newEmails } : h
      );
      setHistory(updatedHistory);

      // Persist to storage
      const { updateHistoryEntry } = await import('./services/storage');
      await updateHistoryEntry(selectedEntry.id, { emails: newEmails });
    }
  };

  const sidebarContent = (
    <>
      <div style={sidebarHeaderStyles}>
        <div style={logoContainerStyles}>
          <div style={logoIconStyles}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <h1 style={logoStyles}>DealFlow</h1>
            <span style={logoSubtitleStyles}>Terminal v2.0</span>
          </div>
        </div>
      </div>

      <div style={navStyles}>
        <NavItem
          label="New Research"
          isActive={view === 'research' && !selectedEntry}
          onClick={() => {
            handleNewResearch();
            setView('research');
          }}
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          }
        />
        <NavItem
          label="History"
          isActive={view === 'history'}
          onClick={() => setView('history')}
          count={history.length}
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <NavItem
          label="Settings"
          isActive={false}
          onClick={() => setShowSettings(true)}
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
            </svg>
          }
        />
      </div>

      <div style={historySectionStyles}>
        <div style={historySectionTitleStyles}>Recent Reports</div>
        <HistoryList
          entries={history.slice(0, 10)}
          onSelect={handleSelectEntry}
          onDelete={handleDeleteEntry}
          selectedId={selectedEntry?.id}
        />
      </div>

      {/* Stats footer */}
      <div style={statsFooterStyles}>
        <div style={statItemStyles}>
          <span style={statValueStyles}>{history.length}</span>
          <span style={statLabelStyles}>Reports</span>
        </div>
        <div style={statItemStyles}>
          <span style={statValueStyles}>
            {history.reduce((acc, h) => acc + Object.keys(h.emails || {}).length, 0)}
          </span>
          <span style={statLabelStyles}>Emails</span>
        </div>
      </div>
    </>
  );

  const mainContent = () => {
    if (view === 'history') {
      return (
        <>
          <Header
            title="Report History"
            subtitle={`${history.length} reports saved`}
          />
          <Content>
            <HistoryList
              entries={history}
              onSelect={handleSelectEntry}
              onDelete={handleDeleteEntry}
              selectedId={selectedEntry?.id}
              variant="full"
            />
          </Content>
        </>
      );
    }

    return (
      <>
        <Header
          title="Company Research"
          subtitle="AI-powered company analysis and outreach"
        />
        <Content>
          <div style={mainGridStyles}>
            <div style={leftColumnStyles}>
              <CompanyInput
                companyName={companyName}
                websiteUrl={websiteUrl}
                onCompanyNameChange={setCompanyName}
                onWebsiteUrlChange={setWebsiteUrl}
                onSubmit={handleResearch}
                loading={loading}
                error={error}
              />

              {loading && <ResearchSkeleton />}

              {research && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                  style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}
                >
                  <ReportPreview
                    company={research}
                    onDownload={handleDownload}
                    onOpenPDF={pdfPath ? handleOpenPDF : undefined}
                    pdfPath={pdfPath}
                  />
                  <MarketPositionChart company={research} />
                </motion.div>
              )}

              {/* Empty state with helpful info */}
              {!research && !loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <GlassCard variant="subtle" padding="xl">
                    <div style={emptyStateContainerStyles}>
                      <div style={emptyStateIconStyles}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="1.5">
                          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>
                      <h3 style={emptyStateTitleStyles}>Start Your Research</h3>
                      <p style={emptyStateTextStyles}>
                        Enter a company name and website URL above to generate a comprehensive analysis report and personalized outreach emails.
                      </p>
                      <div style={featureGridStyles}>
                        <FeatureItem
                          icon="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          title="PDF Reports"
                          desc="Wall Street grade analysis"
                        />
                        <FeatureItem
                          icon="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                          title="Smart Emails"
                          desc="Hyper-personalized outreach"
                        />
                        <FeatureItem
                          icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                          title="Valuations"
                          desc="Industry benchmarks"
                        />
                      </div>
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </div>

            <div style={rightColumnStyles}>
              {research && !loading && (
                <EmailGenerator
                  company={research}
                  initialEmails={emails}
                  onEmailsUpdate={handleEmailsUpdate}
                />
              )}

              {!research && !loading && (
                <GlassCard variant="subtle" padding="xl" style={{ height: '100%' }}>
                  <div style={placeholderStyles}>
                    <div style={placeholderIconStyles}>
                      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="1">
                        <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p style={placeholderTitleStyles}>Email Generator</p>
                    <p style={placeholderTextStyles}>
                      Research a company to generate personalized outreach emails with multiple tones and sequences.
                    </p>
                    <div style={emailPreviewGridStyles}>
                      <div style={emailPreviewItemStyles}>
                        <span style={emailPreviewLabelStyles}>Hook</span>
                        <span style={emailPreviewDescStyles}>Initial outreach</span>
                      </div>
                      <div style={emailPreviewItemStyles}>
                        <span style={emailPreviewLabelStyles}>Value</span>
                        <span style={emailPreviewDescStyles}>Add insights</span>
                      </div>
                      <div style={emailPreviewItemStyles}>
                        <span style={emailPreviewLabelStyles}>Close</span>
                        <span style={emailPreviewDescStyles}>Soft ask</span>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              )}
            </div>
          </div>
        </Content>
      </>
    );
  };

  return (
    <>
      <Layout sidebar={<Sidebar>{sidebarContent}</Sidebar>}>
        {mainContent()}
      </Layout>
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        settings={settings}
        onSave={saveSettings}
      />
    </>
  );
};

// Feature Item Component
const FeatureItem: React.FC<{ icon: string; title: string; desc: string }> = ({ icon, title, desc }) => (
  <div style={featureItemStyles}>
    <div style={featureIconStyles}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="1.5">
        <path d={icon} />
      </svg>
    </div>
    <div>
      <div style={featureTitleStyles}>{title}</div>
      <div style={featureDescStyles}>{desc}</div>
    </div>
  </div>
);

// Styles
const sidebarHeaderStyles: React.CSSProperties = {
  padding: spacing.xl,
  paddingTop: '48px',
  borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
};

const logoContainerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
};

const logoIconStyles: React.CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: borderRadius.lg,
  background: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const logoStyles: React.CSSProperties = {
  fontSize: typography.sizes.lg,
  fontWeight: typography.weights.bold,
  color: colors.textPrimary,
  margin: 0,
  letterSpacing: '-0.5px',
};

const logoSubtitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  display: 'block',
};

const navStyles: React.CSSProperties = {
  padding: `${spacing.lg} 0`,
  borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
};

const historySectionStyles: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  padding: spacing.md,
};

const historySectionTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  fontWeight: typography.weights.semibold,
  color: colors.textMuted,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  padding: `${spacing.sm} ${spacing.md}`,
};

const statsFooterStyles: React.CSSProperties = {
  display: 'flex',
  padding: spacing.lg,
  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
  background: 'rgba(0, 0, 0, 0.2)',
};

const statItemStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '2px',
};

const statValueStyles: React.CSSProperties = {
  fontSize: typography.sizes.xl,
  fontWeight: typography.weights.bold,
  color: colors.textPrimary,
};

const statLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
};

const mainGridStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 420px',
  gap: spacing.xl,
  minHeight: '100%',
};

const leftColumnStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.xl,
  minHeight: 0,
  paddingBottom: spacing.xl,
};

const rightColumnStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  minHeight: 0,
};

const emptyStateContainerStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  padding: spacing.xl,
};

const emptyStateIconStyles: React.CSSProperties = {
  marginBottom: spacing.lg,
  opacity: 0.4,
};

const emptyStateTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.lg,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  marginBottom: spacing.sm,
};

const emptyStateTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
  maxWidth: 400,
  marginBottom: spacing.xl,
  lineHeight: 1.6,
};

const featureGridStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(3, 1fr)',
  gap: spacing.lg,
  width: '100%',
};

const featureItemStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: spacing.sm,
  padding: spacing.md,
  borderRadius: borderRadius.md,
  background: 'rgba(0, 0, 0, 0.2)',
  border: '1px solid rgba(255, 255, 255, 0.06)',
};

const featureIconStyles: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: borderRadius.md,
  background: 'rgba(99, 102, 241, 0.1)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const featureTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textPrimary,
};

const featureDescStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
};

const placeholderStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  height: '100%',
  textAlign: 'center',
  padding: spacing['2xl'],
};

const placeholderIconStyles: React.CSSProperties = {
  marginBottom: spacing.lg,
  opacity: 0.3,
};

const placeholderTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.lg,
  fontWeight: typography.weights.semibold,
  color: colors.textSecondary,
  marginBottom: spacing.sm,
};

const placeholderTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textMuted,
  maxWidth: 280,
  marginBottom: spacing.xl,
  lineHeight: 1.6,
};

const emailPreviewGridStyles: React.CSSProperties = {
  display: 'flex',
  gap: spacing.sm,
  width: '100%',
};

const emailPreviewItemStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '2px',
  padding: spacing.md,
  borderRadius: borderRadius.md,
  background: 'rgba(0, 0, 0, 0.3)',
  border: '1px solid rgba(255, 255, 255, 0.06)',
};

const emailPreviewLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textSecondary,
};

const emailPreviewDescStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
};

export default App;
