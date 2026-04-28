import {
  AbsoluteFill,
  Audio,
  Sequence,
  Series,
  staticFile,
} from "remotion";
import type { FC } from "react";
import { CTA } from "./scenes/CTA";
import { Hook } from "./scenes/Hook";
import { JobCard } from "./scenes/JobCard";
import type { WeeklyJobs } from "./types";

export type JobberMedReelProps = {
  weeklyJobs: WeeklyJobs;
} & Record<string, unknown>;

export const JobberMedReel: FC<JobberMedReelProps> = ({ weeklyJobs }) => {
  const jobs = weeklyJobs.jobs.slice(0, 3);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0A1628",
        color: "#FFFFFF",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <Sequence>
        <Audio src={staticFile("voiceover.mp3")} />
      </Sequence>

      <Series>
        <Series.Sequence durationInFrames={150}>
          <Hook />
        </Series.Sequence>

        {jobs.map((job, index) => (
          <Series.Sequence
            durationInFrames={300}
            key={`${job.title}-${job.company}`}
          >
            <JobCard job={job} number={index + 1} />
          </Series.Sequence>
        ))}

        <Series.Sequence durationInFrames={300}>
          <CTA />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
