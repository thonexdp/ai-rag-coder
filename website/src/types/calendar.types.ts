export interface CalendarEvent {
  id: number;
  title: string;
  description: string | null;
  event_date: string;
}

export interface CalendarEventPayload {
  title: string;
  description?: string;
  event_date: string;
}
