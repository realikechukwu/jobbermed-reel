/* eslint-disable @remotion/warn-native-media-tag */
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { CSSProperties } from "react";
import type { Job } from "../types";

interface JobCardProps {
  job: Job;
  number: number;
}

const staggerStyle = (frame: number, delay: number): CSSProperties => {
  const opacity = interpolate(frame, [delay, delay + 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(opacity, [0, 1], [18, 0]);

  return {
    opacity,
    transform: `translateY(${translateY}px)`,
  };
};

const pillBase: CSSProperties = {
  alignItems: "center",
  backgroundColor: "#1E3A5F",
  borderRadius: 999,
  display: "inline-flex",
  fontSize: 26,
  fontWeight: 700,
  justifyContent: "center",
  lineHeight: 1.2,
  padding: "14px 28px",
  whiteSpace: "nowrap",
};

export const JobCard = ({ job, number }: JobCardProps) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const cardProgress = spring({
    frame,
    fps,
    config: {
      damping: 13,
      mass: 0.85,
      stiffness: 118,
    },
  });
  const translateX = interpolate(cardProgress, [0, 1], [520, 0]);
  const cardOpacity = interpolate(frame, [0, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cardWidth = width - 120;

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        backgroundColor: "#0A1628",
        display: "flex",
        justifyContent: "center",
        overflow: "hidden",
        padding: "220px 60px 116px",
      }}
    >
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 84% 24%, rgba(0, 180, 216, 0.1), rgba(0, 180, 216, 0) 34%), radial-gradient(circle at 12% 78%, rgba(0, 180, 216, 0.06), rgba(0, 180, 216, 0) 36%)",
        }}
      />

      <img
        alt="JobberMed"
        src={staticFile("jobbermed-logo.png")}
        style={{
          height: 70,
          left: 60,
          position: "absolute",
          top: 60,
          zIndex: 2,
        }}
      />

      <div
        style={{
          height: "100%",
          opacity: cardOpacity,
          position: "relative",
          transform: `translateX(${translateX}px)`,
          width: cardWidth,
          zIndex: 1,
        }}
      >
        <div
          style={{
            backgroundColor: "#132845",
            border: "1px solid rgba(0, 180, 216, 0.3)",
            borderRadius: 32,
            boxShadow: "0 30px 90px rgba(0, 0, 0, 0.24)",
            display: "flex",
            flexDirection: "column",
            height: "100%",
            padding: 64,
          }}
        >
          <div
            style={{
              ...staggerStyle(frame, 24),
              alignItems: "center",
              color: "#00B4D8",
              display: "flex",
              fontSize: 28,
              fontWeight: 800,
              letterSpacing: 3,
              lineHeight: 1.3,
              marginLeft: 120,
              minHeight: 80,
              textTransform: "uppercase",
            }}
          >
            NOW HIRING
          </div>

          <h2
            style={{
              ...staggerStyle(frame, 30),
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 2,
              color: "#FFFFFF",
              display: "-webkit-box",
              fontSize: 88,
              fontWeight: 800,
              lineHeight: 1.1,
              margin: "52px 0 0",
              overflow: "hidden",
            }}
          >
            {job.title}
          </h2>

          <div
            style={{
              ...staggerStyle(frame, 36),
              color: "#8899AA",
              fontSize: 72,
              fontWeight: 600,
              lineHeight: 1.45,
              marginTop: 32,
            }}
          >
            {job.company}
          </div>

          <div
            style={{
              ...staggerStyle(frame, 42),
              color: "#FFFFFF",
              fontSize: 72,
              fontWeight: 600,
              lineHeight: 1.45,
              marginTop: 44,
            }}
          >
            📍 {job.location}
          </div>

          <div
            style={{
              ...staggerStyle(frame, 48),
              display: "flex",
              flexWrap: "wrap",
              gap: 18,
              marginTop: 48,
            }}
          >
            <div
              style={{
                ...pillBase,
                color: "#00B4D8",
              }}
            >
              Deadline: {job.deadline}
            </div>
            <div
              style={{
                ...pillBase,
                color: "#FFFFFF",
              }}
            >
              {job.type}
            </div>
          </div>

          <div style={{ flex: 1 }} />

          <div
            style={{
              ...staggerStyle(frame, 58),
              backgroundColor: "rgba(0, 180, 216, 0.65)",
              height: 1,
              marginTop: 72,
              width: "100%",
            }}
          />

          <div
            style={{
              ...staggerStyle(frame, 64),
              color: "#00B4D8",
              fontSize: 28,
              fontWeight: 800,
              lineHeight: 1.4,
              marginTop: 28,
            }}
          >
            Tap link in bio to apply →
          </div>
        </div>
        <div
          style={{
            alignItems: "center",
            backgroundColor: "#00B4D8",
            borderRadius: "50%",
            boxShadow: "0 18px 46px rgba(0, 180, 216, 0.28)",
            color: "#FFFFFF",
            display: "flex",
            fontSize: 42,
            fontWeight: 800,
            height: 80,
            justifyContent: "center",
            left: 64,
            position: "absolute",
            top: 64,
            width: 80,
            zIndex: 2,
          }}
        >
          {number}
        </div>
      </div>

      <div
        style={{
          bottom: 40,
          color: "#8899AA",
          fontSize: 28,
          fontWeight: 600,
          left: 0,
          lineHeight: 1.2,
          position: "absolute",
          right: 0,
          textAlign: "center",
          zIndex: 2,
        }}
      >
        www.jobbermed.com
      </div>
    </AbsoluteFill>
  );
};
