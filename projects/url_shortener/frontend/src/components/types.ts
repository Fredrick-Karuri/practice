export interface ShortenResponse{
  short_url:string
  short_code:string
}

export interface StatsResponse{
  short_code:string
  long_url:string
  clicks:number
  created_at:string
  last_clicked_at:string | null

}