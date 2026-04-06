import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import api from '../api/client'

interface User {
  id: number
  phone: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

const loadFromStorage = (): Partial<AuthState> => {
  try {
    const access = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')
    const userStr = localStorage.getItem('user')
    if (access && refresh) {
      const state: Partial<AuthState> = {
        accessToken: access,
        refreshToken: refresh,
        isAuthenticated: true,
      }
      if (userStr) {
        try {
          state.user = JSON.parse(userStr)
        } catch {}
      }
      return state
    }
  } catch (e) {
    console.warn('Failed to load auth from storage:', e)
  }
  return {}
}

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  ...loadFromStorage(),
}

export const login = createAsyncThunk(
  'auth/login',
  async ({ phone, password }: { phone: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login/', { phone, password })
      const { access, refresh, user } = response.data
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      return { user, access, refresh }
    } catch (error: any) {
      const message = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || 'Ошибка входа'
      return rejectWithValue(message)
    }
  }
)

export const sendSms = createAsyncThunk(
  'auth/sendSms',
  async (phone: string, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/sms/send/', { phone })
      return response.data
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Ошибка отправки кода'
      return rejectWithValue(message)
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async ({ phone, password, sms_code, first_name, last_name, referral_code }: {
    phone: string
    password: string
    sms_code?: string
    first_name?: string
    last_name?: string
    referral_code?: string
  }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/register/', {
        phone,
        password,
        sms_code,
        first_name,
        last_name,
        referral_code,
      })
      const { access, refresh, user } = response.data
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      return { user, access, refresh }
    } catch (error: any) {
      const message = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || 'Ошибка регистрации'
      return rejectWithValue(message)
    }
  }
)

export const fetchProfile = createAsyncThunk('auth/fetchProfile', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get('/auth/profile/')
    return response.data
  } catch (error: any) {
    return rejectWithValue('Не удалось загрузить профиль')
  }
})

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.user = action.payload.user
        state.accessToken = action.payload.access
        state.refreshToken = action.payload.refresh
        state.isAuthenticated = true
        state.isLoading = false
        state.error = null
        try { localStorage.setItem('user', JSON.stringify(action.payload.user)) } catch {}
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(register.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.user = action.payload.user
        state.accessToken = action.payload.access
        state.refreshToken = action.payload.refresh
        state.isAuthenticated = true
        state.isLoading = false
        state.error = null
        try { localStorage.setItem('user', JSON.stringify(action.payload.user)) } catch {}
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchProfile.pending, (state) => {
        state.isLoading = true
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.user = action.payload
        state.isAuthenticated = true
        state.isLoading = false
        try { localStorage.setItem('user', JSON.stringify(action.payload)) } catch {}
      })
      .addCase(fetchProfile.rejected, (state) => {
        state.isLoading = false
        state.isAuthenticated = false
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.accessToken = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.error = null
        try { localStorage.removeItem('user') } catch {}
      })
  },
})

export const { setUser, clearError } = authSlice.actions
export default authSlice.reducer
