import { createI18n } from 'vue-i18n'
import en from '@/locale/en/en.json'
import zh_tw from '@/locale/zh_tw/zh_tw.json'

const savedLocale = localStorage.getItem('locale') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, zh_tw },
})

export default i18n
