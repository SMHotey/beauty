import toast from 'react-hot-toast'

export function handleApiError(error: unknown, defaultMessage = 'Произошла ошибка'): void {
  console.error(error)
  
  if (error && typeof error === 'object' && 'response' in error) {
    const err = error as { response?: { data?: { detail?: string; non_field_errors?: string[] } } }
    const message = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0]
    if (message) {
      toast.error(message)
      return
    }
  }
  
  toast.error(defaultMessage)
}
