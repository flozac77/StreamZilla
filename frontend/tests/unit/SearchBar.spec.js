import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SearchBar from '@/components/SearchBar.vue'
import { useVideoStore } from '@/stores/videoStore'

describe('SearchBar.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    wrapper = mount(SearchBar, {
      global: {
        plugins: [createTestingPinia()]
      }
    })
    store = useVideoStore()
  })

  it('renders properly', () => {
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('updates searchQuery on input', async () => {
    const input = wrapper.find('input')
    await input.setValue('Minecraft')
    expect(input.element.value).toBe('Minecraft')
  })

  it('calls searchVideos on button click', async () => {
    const input = wrapper.find('input')
    await input.setValue('Minecraft')
    await wrapper.find('button').trigger('click')
    expect(store.searchVideos).toHaveBeenCalledWith('Minecraft')
  })

  it('debounces search on input', async () => {
    jest.useFakeTimers()
    const input = wrapper.find('input')
    await input.setValue('Mine')
    await input.setValue('Minec')
    await input.setValue('Minecraft')
    
    jest.advanceTimersByTime(500)
    expect(store.searchVideos).toHaveBeenCalledTimes(1)
    expect(store.searchVideos).toHaveBeenCalledWith('Minecraft')
  })
}) 