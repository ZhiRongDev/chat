import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import App from '../App.vue'

describe('App', () => {
  let pinia: any
  let router: any

  beforeEach(() => {
    pinia = createPinia()
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: { template: '<div>Home</div>' },
        },
      ],
    })
  })

  it('renders properly', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has router-view component', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })
    expect(wrapper.html()).toContain('router-view')
  })
})
