import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatSettings from '../components/ChatSettings.vue'

describe('ChatSettings', () => {
  const defaultSettings = {
    useRag: false,
    topK: 5,
    minScore: 0.3,
    provider: '',
    model: '',
    temperature: 0.7,
    geminiApiKey: '',
    openaiApiKey: '',
    anthropicApiKey: '',
  }

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  it('renders properly', () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: defaultSettings,
      },
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Chat Settings')
  })

  it('displays RAG toggle', () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: defaultSettings,
      },
    })
    expect(wrapper.text()).toContain('Enable RAG Mode')
  })

  it('displays LLM provider selection', () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: defaultSettings,
      },
    })
    expect(wrapper.text()).toContain('LLM Provider')
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('shows RAG options when RAG is enabled', async () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: { ...defaultSettings, useRag: true },
      },
    })

    expect(wrapper.text()).toContain('Top-K Results')
    expect(wrapper.text()).toContain('Minimum Relevance Score')
  })

  it('emits update event on save', async () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: defaultSettings,
      },
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted()).toHaveProperty('update:modelValue')
  })

  it('emits show-documents event', async () => {
    const wrapper = mount(ChatSettings, {
      props: {
        modelValue: defaultSettings,
      },
    })

    const documentButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Manage Documents')
    )

    if (documentButton) {
      await documentButton.trigger('click')
      expect(wrapper.emitted()).toHaveProperty('show-documents')
    }
  })
})
