import { createApp } from 'vue'
import { createPinia } from 'pinia'
import i18n from '@/utils/i18n'
import { setLocale } from './utils/locale'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'highlight.js/styles/github.css' // Syntax highlighting theme
import './assets/styles/scss/main.scss'

import App from './App.vue'
import router from './router'

setLocale('zh_tw')

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
