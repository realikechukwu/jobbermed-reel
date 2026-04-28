export interface Job {
  title: string;
  company: string;
  location: string;
  deadline: string;
  type: string;
}

export interface WeeklyJobs {
  weekOf: string;
  jobs: Job[];
}
