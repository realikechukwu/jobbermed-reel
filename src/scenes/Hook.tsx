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

const fadeSlide = (
  frame: number,
  delay: number,
  distance: number,
): CSSProperties => {
  const opacity = interpolate(frame, [delay, delay + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(opacity, [0, 1], [distance, 0]);

  return {
    opacity,
    transform: `translateY(${translateY}px)`,
  };
};

export const Hook = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stagger = Math.round(fps * 0.2);
  const logoProgress = spring({
    frame,
    fps,
    config: {
      damping: 18,
      mass: 0.7,
      stiffness: 90,
    },
  });
  const logoOpacity = interpolate(frame, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulseOpacity = 0.025 + Math.sin(frame / 15) * 0.025;

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        backgroundColor: "#0A1628",
        display: "flex",
        justifyContent: "center",
        overflow: "hidden",
        padding: 60,
      }}
    >
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 44%, rgba(0, 180, 216, ${pulseOpacity}) 0%, rgba(0, 180, 216, 0) 58%)`,
        }}
      />

      <img
        alt="JobberMed"
        src={staticFile("jobbermed-logo.png")}
        style={{
          left: 60,
          height: 70,
          opacity: logoOpacity,
          position: "absolute",
          top: 60,
          transform: `scale(${interpolate(logoProgress, [0, 1], [0.94, 1])})`,
        }}
      />

      <div
        style={{
          alignItems: "center",
          display: "flex",
          flexDirection: "column",
          gap: 42,
          textAlign: "center",
          width: "100%",
          zIndex: 1,
        }}
      >
        <div
          style={{
            ...fadeSlide(frame, stagger, 26),
            color: "#00B4D8",
            fontSize: 32,
            fontWeight: 700,
            letterSpacing: 4,
            lineHeight: 1.35,
            textTransform: "uppercase",
          }}
        >
          THIS WEEK IN JOBBERMED JOBS
        </div>

        <h1
          style={{
            ...fadeSlide(frame, stagger * 2, 34),
            color: "#FFFFFF",
            fontSize: 96,
            fontWeight: 800,
            lineHeight: 1.1,
            margin: 0,
            maxWidth: 900,
          }}
        >
          <span style={{ display: "block" }}>3 Jobs You</span>
          <span style={{ display: "block" }}>Shouldn't Miss</span>
        </h1>
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
          zIndex: 1,
        }}
      >
        www.jobbermed.com
      </div>
    </AbsoluteFill>
  );
};
