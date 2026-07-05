export interface Announcement {
  id: number;
  title: string;
  content: string;
  published_at: string;
}

export interface AnnouncementPayload {
  title: string;
  content: string;
  published_at?: string;
}
