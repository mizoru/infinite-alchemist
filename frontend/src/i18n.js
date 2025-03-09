import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import translationEN from './locales/en/translation.json';
import translationRU from './locales/ru/translation.json';

// Resources for i18next
const resources = {
  en: {
    translation: translationEN
  },
  ru: {
    translation: translationRU
  }
};

// Get language from localStorage or use browser language
const getInitialLanguage = () => {
  const savedLanguage = localStorage.getItem('infinite-alchemist-settings');
  if (savedLanguage) {
    try {
      const settings = JSON.parse(savedLanguage);
      if (settings.state && settings.state.language) {
        return settings.state.language;
      }
    } catch (e) {
      console.error('Error parsing saved language:', e);
    }
  }
  
  // Fallback to browser language or English
  const browserLang = navigator.language.split('-')[0];
  return ['en', 'ru'].includes(browserLang) ? browserLang : 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes values
    }
  });

export default i18n; 