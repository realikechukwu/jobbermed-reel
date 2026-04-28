import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";

import { Composition } from "remotion";
import { z } from "zod";
import weeklyJobs from "../public/weekly-jobs.json";
import type { WeeklyJobs } from "./types";
import { JobberMedReel, type JobberMedReelProps } from "./Video";

const jobSchema = z.object({
  title: z.string(),
  company: z.string(),
  location: z.string(),
  deadline: z.string(),
  type: z.string(),
});

const weeklyJobsSchema = z.object({
  weekOf: z.string(),
  jobs: z.array(jobSchema),
});

const jobberMedReelSchema = z.object({
  weeklyJobs: weeklyJobsSchema,
});

const weeklyJobsData = weeklyJobs as WeeklyJobs;

export const RemotionRoot = () => {
  return (
    <Composition<typeof jobberMedReelSchema, JobberMedReelProps>
      id="JobberMedReel"
      component={JobberMedReel}
      durationInFrames={1350}
      fps={30}
      width={1080}
      height={1920}
      schema={jobberMedReelSchema}
      defaultProps={{
        weeklyJobs: weeklyJobsData,
      }}
    />
  );
};
