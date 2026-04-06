import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface BookingService {
  id: number
  name: string
  price: number
  duration: number
}

export interface BookingState {
  step: number
  selectedServices: BookingService[]
  selectedMaster: number | null
  selectedDate: string | null
  selectedSlot: string | null
  clientPhone: string
  clientName: string
  comment: string
  useBonuses: boolean
}

const initialState: BookingState = {
  step: 1,
  selectedServices: [],
  selectedMaster: null,
  selectedDate: null,
  selectedSlot: null,
  clientPhone: '',
  clientName: '',
  comment: '',
  useBonuses: false,
}

const bookingSlice = createSlice({
  name: 'booking',
  initialState,
  reducers: {
    nextStep: (state) => { state.step = Math.min(state.step + 1, 5) },
    prevStep: (state) => { state.step = Math.max(state.step - 1, 1) },
    setStep: (state, action: PayloadAction<number>) => { state.step = action.payload },
    addService: (state, action: PayloadAction<BookingService>) => {
      if (!state.selectedServices.find(s => s.id === action.payload.id)) {
        state.selectedServices.push(action.payload)
      }
    },
    removeService: (state, action: PayloadAction<number>) => {
      state.selectedServices = state.selectedServices.filter(s => s.id !== action.payload)
    },
    clearServices: (state) => { state.selectedServices = [] },
    setMaster: (state, action: PayloadAction<number>) => { state.selectedMaster = action.payload },
    setDate: (state, action: PayloadAction<string>) => { state.selectedDate = action.payload },
    setSlot: (state, action: PayloadAction<string>) => { state.selectedSlot = action.payload },
    setClientPhone: (state, action: PayloadAction<string>) => { state.clientPhone = action.payload },
    setClientName: (state, action: PayloadAction<string>) => { state.clientName = action.payload },
    setComment: (state, action: PayloadAction<string>) => { state.comment = action.payload },
    setUseBonuses: (state, action: PayloadAction<boolean>) => { state.useBonuses = action.payload },
    resetBooking: (state) => {
      Object.assign(state, initialState)
    },
  },
})

export const {
  nextStep, prevStep, setStep, addService, removeService, clearServices,
  setMaster, setDate, setSlot, setClientPhone, setClientName, setComment,
  setUseBonuses, resetBooking,
} = bookingSlice.actions
export default bookingSlice.reducer
