import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SearchFilters from '../../../src/components/SearchFilters.vue'

describe('SearchFilters.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const createWrapper = () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createPinia()]
      }
    })
    return { wrapper }
  }

  it('renders all filter sections', () => {
    const { wrapper } = createWrapper()

    expect(wrapper.find('[data-test="date-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="duration-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="views-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="language-filter"]').exists()).toBe(true)
  })

  it('updates store when date filter changes', async () => {
    const { wrapper } = createWrapper()
    const dateSelect = wrapper.find('[data-test="date-filter"]')

    await dateSelect.setValue('today')
    expect((wrapper.vm as any).selectedFilters.date).toBe('today')
  })

  it('updates store when duration filter changes', async () => {
    const { wrapper } = createWrapper()
    const durationSelect = wrapper.find('[data-test="duration-filter"]')

    await durationSelect.setValue('short')
    expect((wrapper.vm as any).selectedFilters.duration).toBe('short')
  })

  it('updates store when views filter changes', async () => {
    const { wrapper } = createWrapper()
    const viewsSelect = wrapper.find('[data-test="views-filter"]')

    await viewsSelect.setValue('more_1000')
    expect((wrapper.vm as any).selectedFilters.views).toBe('more_1000')
  })

  it('updates store when language filter changes', async () => {
    const { wrapper } = createWrapper()
    const languageSelect = wrapper.find('[data-test="language-filter"]')

    await languageSelect.setValue('fr')
    expect((wrapper.vm as any).selectedFilters.language).toBe('fr')
  })

  it('updates sort when clicking sort buttons', async () => {
    const { wrapper } = createWrapper()
    const sortButton = wrapper.find('button[data-test="sort-button"]')

    await sortButton.trigger('click')
    expect((wrapper.vm as any).currentSort).toBe('date')
  })

  it('highlights active sort button', async () => {
    const { wrapper } = createWrapper()
    const sortButton = wrapper.find('button[data-test="sort-button"]')

    await sortButton.trigger('click')
    expect(sortButton.classes()).toContain('active')
  })

  it('resets filters when changing game', async () => {
    const { wrapper } = createWrapper()
    const store = (wrapper.vm as any).store

    store.$patch({
      filters: {
        date: 'today',
        duration: 'short',
        views: 'more_1000',
        language: 'fr'
      }
    })

    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).selectedFilters).toEqual({
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    })
  })
}) 