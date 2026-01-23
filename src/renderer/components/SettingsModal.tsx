import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui';
import { colors, typography, spacing, borderRadius } from '../styles/theme';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: UserSettings;
  onSave: (settings: UserSettings) => void;
}

export type AIProvider = 'openrouter' | 'openai' | 'anthropic' | 'gemini';

export interface UserSettings {
  userName: string;
  defaultTone: 'formal' | 'friendly' | 'direct';
  companyName: string;
  aiProvider: AIProvider;
  apiKey: string;
}

const AI_PROVIDERS: { id: AIProvider; name: string; placeholder: string; hint: string; url: string }[] = [
  {
    id: 'openrouter',
    name: 'OpenRouter',
    placeholder: 'sk-or-v1-...',
    hint: 'Access to 100+ models including GPT-4, Claude, Gemini',
    url: 'https://openrouter.ai/keys',
  },
  {
    id: 'openai',
    name: 'OpenAI',
    placeholder: 'sk-...',
    hint: 'GPT-4o, GPT-4 Turbo, GPT-3.5',
    url: 'https://platform.openai.com/api-keys',
  },
  {
    id: 'anthropic',
    name: 'Anthropic (Claude)',
    placeholder: 'sk-ant-...',
    hint: 'Claude 3.5 Sonnet, Claude 3 Opus',
    url: 'https://console.anthropic.com/settings/keys',
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    placeholder: 'AIza...',
    hint: 'Gemini 1.5 Pro, Gemini 1.5 Flash',
    url: 'https://aistudio.google.com/app/apikey',
  },
];

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSave,
}) => {
  const [userName, setUserName] = useState(settings.userName);
  const [defaultTone, setDefaultTone] = useState(settings.defaultTone);
  const [companyName, setCompanyName] = useState(settings.companyName);
  const [aiProvider, setAiProvider] = useState<AIProvider>(settings.aiProvider || 'openrouter');
  const [apiKey, setApiKey] = useState(settings.apiKey || '');
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    setUserName(settings.userName);
    setDefaultTone(settings.defaultTone);
    setCompanyName(settings.companyName);
    setAiProvider(settings.aiProvider || 'openrouter');
    setApiKey(settings.apiKey || '');
  }, [settings]);

  const handleSave = () => {
    onSave({ userName, defaultTone, companyName, aiProvider, apiKey });
    onClose();
  };

  const selectedProvider = AI_PROVIDERS.find(p => p.id === aiProvider) || AI_PROVIDERS[0];

  const tones = [
    { id: 'formal' as const, label: 'Formal', desc: 'Professional and polished' },
    { id: 'friendly' as const, label: 'Friendly', desc: 'Warm but professional' },
    { id: 'direct' as const, label: 'Direct', desc: 'Concise and to-the-point' },
  ];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <div style={overlayStyles}>
          {/* Backdrop */}
          <motion.div
            style={backdropStyles}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal - Centered */}
          <motion.div
            style={modalWrapperStyles}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
          >
            <div style={modalStyles}>
              {/* Top highlight */}
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '1px',
                background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
                pointerEvents: 'none',
              }} />

              {/* Header */}
              <div style={headerStyles}>
                <div style={headerIconStyles}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                  </svg>
                </div>
                <div style={{ flex: 1 }}>
                  <h2 style={titleStyles}>Settings</h2>
                  <p style={subtitleStyles}>Configure your preferences</p>
                </div>
                <button style={closeButtonStyles} onClick={onClose}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Scrollable Content */}
              <div style={contentStyles}>
                {/* AI Provider Section */}
                <div style={sectionStyles}>
                  <div style={sectionHeaderStyles}>
                    <div style={{ ...sectionIconStyles, background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.cyan} strokeWidth="2">
                        <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
                      </svg>
                    </div>
                    <div>
                      <h3 style={sectionTitleStyles}>AI Provider</h3>
                      <p style={sectionDescStyles}>Choose your AI service and enter your API key</p>
                    </div>
                  </div>

                  {/* Provider Selection */}
                  <div style={fieldGroupStyles}>
                    <label style={labelStyles}>Provider</label>
                    <div style={providerGridStyles}>
                      {AI_PROVIDERS.map((provider) => (
                        <button
                          key={provider.id}
                          style={providerButtonStyles(aiProvider === provider.id)}
                          onClick={() => setAiProvider(provider.id)}
                        >
                          <div style={providerRadioStyles(aiProvider === provider.id)}>
                            {aiProvider === provider.id && (
                              <motion.div
                                style={providerRadioInnerStyles}
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ duration: 0.15 }}
                              />
                            )}
                          </div>
                          <div style={providerInfoStyles}>
                            <span style={providerNameStyles}>{provider.name}</span>
                            <span style={providerHintStyles}>{provider.hint}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* API Key Input */}
                  <div style={fieldGroupStyles}>
                    <label style={labelStyles}>{selectedProvider.name} API Key</label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showApiKey ? 'text' : 'password'}
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder={selectedProvider.placeholder}
                        style={{ ...inputStyles, paddingRight: '44px' }}
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        style={toggleButtonStyles}
                      >
                        {showApiKey ? (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
                            <line x1="1" y1="1" x2="23" y2="23" />
                          </svg>
                        ) : (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                            <circle cx="12" cy="12" r="3" />
                          </svg>
                        )}
                      </button>
                    </div>
                    <p style={hintStyles}>
                      Get your API key from{' '}
                      <a href={selectedProvider.url} target="_blank" rel="noopener noreferrer" style={linkStyles}>
                        {selectedProvider.url.replace('https://', '').split('/')[0]}
                      </a>
                    </p>
                  </div>

                  {/* Status indicator */}
                  {apiKey && (
                    <div style={statusBoxStyles}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.emerald} strokeWidth="2">
                        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                        <polyline points="22 4 12 14.01 9 11.01" />
                      </svg>
                      <span>API key configured for {selectedProvider.name}</span>
                    </div>
                  )}
                </div>

                {/* User Profile Section */}
                <div style={sectionStyles}>
                  <div style={sectionHeaderStyles}>
                    <div style={sectionIconStyles}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    </div>
                    <div>
                      <h3 style={sectionTitleStyles}>User Profile</h3>
                      <p style={sectionDescStyles}>Used to sign your emails</p>
                    </div>
                  </div>

                  <div style={fieldGroupStyles}>
                    <label style={labelStyles}>Your Name</label>
                    <input
                      type="text"
                      value={userName}
                      onChange={(e) => setUserName(e.target.value)}
                      placeholder="e.g., John Smith"
                      style={inputStyles}
                    />
                  </div>

                  <div style={fieldGroupStyles}>
                    <label style={labelStyles}>Company / Firm Name</label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="e.g., EAI Capital"
                      style={inputStyles}
                    />
                  </div>
                </div>

                {/* Email Preferences Section */}
                <div style={sectionStyles}>
                  <div style={sectionHeaderStyles}>
                    <div style={{ ...sectionIconStyles, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.emerald} strokeWidth="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                        <polyline points="22,6 12,13 2,6" />
                      </svg>
                    </div>
                    <div>
                      <h3 style={sectionTitleStyles}>Email Preferences</h3>
                      <p style={sectionDescStyles}>Default tone for generated emails</p>
                    </div>
                  </div>

                  <div style={toneGridStyles}>
                    {tones.map((tone) => (
                      <button
                        key={tone.id}
                        style={toneButtonStyles(defaultTone === tone.id)}
                        onClick={() => setDefaultTone(tone.id)}
                      >
                        <div style={toneRadioStyles(defaultTone === tone.id)}>
                          {defaultTone === tone.id && (
                            <motion.div
                              style={toneRadioInnerStyles}
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              transition={{ duration: 0.15 }}
                            />
                          )}
                        </div>
                        <div style={toneLabelContainerStyles}>
                          <span style={toneLabelStyles}>{tone.label}</span>
                          <span style={toneDescStyles}>{tone.desc}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div style={footerStyles}>
                <Button variant="secondary" onClick={onClose}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleSave}>
                  Save Settings
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

// Styles
const overlayStyles: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const backdropStyles: React.CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'rgba(0, 0, 0, 0.7)',
  backdropFilter: 'blur(8px)',
  WebkitBackdropFilter: 'blur(8px)',
};

const modalWrapperStyles: React.CSSProperties = {
  position: 'relative',
  width: '100%',
  maxWidth: 560,
  maxHeight: '90vh',
  margin: spacing.xl,
};

const modalStyles: React.CSSProperties = {
  position: 'relative',
  background: 'rgba(14, 17, 23, 0.95)',
  backdropFilter: 'blur(24px)',
  WebkitBackdropFilter: 'blur(24px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: borderRadius['2xl'],
  boxShadow: '0 24px 80px rgba(0, 0, 0, 0.6), inset 0 0 0 1px rgba(255, 255, 255, 0.05)',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  maxHeight: '85vh',
};

const headerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
  padding: spacing.xl,
  borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
  flexShrink: 0,
};

const headerIconStyles: React.CSSProperties = {
  width: 44,
  height: 44,
  borderRadius: borderRadius.lg,
  background: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const titleStyles: React.CSSProperties = {
  fontSize: typography.sizes.lg,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  margin: 0,
};

const subtitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textMuted,
  margin: 0,
  marginTop: '2px',
};

const closeButtonStyles: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: borderRadius.md,
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: colors.textMuted,
  cursor: 'pointer',
};

const contentStyles: React.CSSProperties = {
  padding: spacing.xl,
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.xl,
  overflowY: 'auto',
  flex: 1,
};

const sectionStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.md,
};

const sectionHeaderStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.md,
  marginBottom: spacing.xs,
};

const sectionIconStyles: React.CSSProperties = {
  width: 32,
  height: 32,
  borderRadius: borderRadius.md,
  background: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
};

const sectionTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  margin: 0,
};

const sectionDescStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  margin: 0,
  marginTop: '2px',
};

const fieldGroupStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.xs,
};

const labelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  fontWeight: typography.weights.medium,
  color: colors.textSecondary,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const inputStyles: React.CSSProperties = {
  width: '100%',
  padding: `${spacing.md} ${spacing.lg}`,
  borderRadius: borderRadius.md,
  background: 'rgba(0, 0, 0, 0.3)',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  color: colors.textPrimary,
  fontSize: typography.sizes.sm,
  outline: 'none',
  transition: 'border-color 0.15s ease',
};

const toggleButtonStyles: React.CSSProperties = {
  position: 'absolute',
  right: '12px',
  top: '50%',
  transform: 'translateY(-50%)',
  background: 'transparent',
  border: 'none',
  color: colors.textMuted,
  cursor: 'pointer',
  padding: '4px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const hintStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  marginTop: spacing.xs,
};

const linkStyles: React.CSSProperties = {
  color: colors.cyan,
  textDecoration: 'none',
};

const providerGridStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: spacing.sm,
};

const providerButtonStyles = (isActive: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.sm,
  padding: spacing.md,
  borderRadius: borderRadius.md,
  background: isActive ? 'rgba(6, 182, 212, 0.1)' : 'rgba(0, 0, 0, 0.2)',
  border: `1px solid ${isActive ? 'rgba(6, 182, 212, 0.3)' : 'rgba(255, 255, 255, 0.06)'}`,
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'all 0.15s ease',
});

const providerRadioStyles = (isActive: boolean): React.CSSProperties => ({
  width: 16,
  height: 16,
  borderRadius: '50%',
  border: `2px solid ${isActive ? colors.cyan : 'rgba(255, 255, 255, 0.2)'}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
  marginTop: '2px',
});

const providerRadioInnerStyles: React.CSSProperties = {
  width: 6,
  height: 6,
  borderRadius: '50%',
  background: colors.cyan,
};

const providerInfoStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '2px',
};

const providerNameStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textPrimary,
};

const providerHintStyles: React.CSSProperties = {
  fontSize: '10px',
  color: colors.textMuted,
  lineHeight: 1.3,
};

const statusBoxStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.sm,
  padding: spacing.md,
  background: 'rgba(16, 185, 129, 0.1)',
  border: '1px solid rgba(16, 185, 129, 0.2)',
  borderRadius: borderRadius.md,
  fontSize: typography.sizes.xs,
  color: colors.emerald,
};

const toneGridStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.sm,
};

const toneButtonStyles = (isActive: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
  padding: spacing.md,
  borderRadius: borderRadius.md,
  background: isActive ? 'rgba(99, 102, 241, 0.1)' : 'rgba(0, 0, 0, 0.2)',
  border: `1px solid ${isActive ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.06)'}`,
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'all 0.15s ease',
});

const toneRadioStyles = (isActive: boolean): React.CSSProperties => ({
  width: 18,
  height: 18,
  borderRadius: '50%',
  border: `2px solid ${isActive ? colors.primary : 'rgba(255, 255, 255, 0.2)'}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
});

const toneRadioInnerStyles: React.CSSProperties = {
  width: 8,
  height: 8,
  borderRadius: '50%',
  background: colors.primary,
};

const toneLabelContainerStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '2px',
};

const toneLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textPrimary,
};

const toneDescStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
};

const footerStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'flex-end',
  gap: spacing.md,
  padding: spacing.xl,
  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
  background: 'rgba(0, 0, 0, 0.2)',
  flexShrink: 0,
};
