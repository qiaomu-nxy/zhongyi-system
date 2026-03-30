import api from './index'

export interface Schedule {
  id: number
  weekday: number
  is_working: boolean
  morning_start: string | null
  morning_end: string | null
  afternoon_start: string | null
  afternoon_end: string | null
  slot_duration: number
}

export interface ScheduleOverride {
  id: number
  override_date: string
  is_working: boolean
  morning_start: string | null
  morning_end: string | null
  afternoon_start: string | null
  afternoon_end: string | null
  slot_duration: number | null
  reason: string | null
}

export const getSchedules = () =>
  api.get<Schedule[]>('/api/v1/schedules')

export const updateSchedule = (data: Partial<Schedule> & { weekday: number }) =>
  api.put<Schedule>('/api/v1/schedules', data)

export const getScheduleOverrides = () =>
  api.get<ScheduleOverride[]>('/api/v1/schedule-overrides')

export const createOverride = (data: Partial<ScheduleOverride> & { override_date: string }) =>
  api.post<ScheduleOverride>('/api/v1/schedule-overrides', data)

export const deleteOverride = (id: number) =>
  api.delete(`/api/v1/schedule-overrides/${id}`)
