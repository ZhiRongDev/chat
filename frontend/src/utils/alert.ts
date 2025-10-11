export function appendAlert(
  message: string,
  type: 'success' | 'danger' | 'warning' | 'info' = 'info',
): void {
  const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
  if (!alertPlaceholder) {
    console.warn('⚠️ No element with id="liveAlertPlaceholder" found.')
    return
  }

  // Create wrapper element
  const wrapper = document.createElement('div')
  wrapper.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      <p class="alert_msg mb-0">${message}</p>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `.trim()

  // Append to placeholder
  alertPlaceholder.append(wrapper)

  // Auto-remove after 6 seconds
  setTimeout(() => {
    wrapper.remove()
  }, 6000)
}
