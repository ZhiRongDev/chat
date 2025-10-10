import i18n from '@/utils/i18n'

export function setLocale(locale: string) {
  localStorage.setItem('locale', locale)
}

export function t(key: string) {
  return i18n.global.t(key)
}

export function getCurrentLocale() {
  return i18n.global.locale.value
}
