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

const fadeUp = (frame: number, delay: number): CSSProperties => {
  const opacity = interpolate(frame, [delay, delay + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(opacity, [0, 1], [22, 0]);

  return {
    opacity,
    transform: `translateY(${translateY}px)`,
  };
};

export const CTA = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoSpring = spring({
    frame: Math.max(0, frame - 4),
    fps,
    config: {
      damping: 14,
      mass: 0.8,
      stiffness: 115,
    },
  });
  const logoOpacity = interpolate(frame, [2, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const logoY = interpolate(logoSpring, [0, 1], [-80, 0]);

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        backgroundColor: "#0A1628",
        display: "flex",
        justifyContent: "center",
        overflow: "hidden",
        padding: 72,
        textAlign: "center",
      }}
    >
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 28%, rgba(0, 180, 216, 0.18), rgba(0, 180, 216, 0) 40%), linear-gradient(180deg, rgba(0, 180, 216, 0.08), rgba(10, 22, 40, 0) 46%)",
        }}
      />

      <div
        style={{
          alignItems: "center",
          display: "flex",
          flexDirection: "column",
          position: "relative",
          width: "100%",
          zIndex: 1,
        }}
      >
        <img
          alt="JobberMed"
          src={staticFile("jobbermed-logo.png")}
          style={{
            height: 160,
            marginBottom: 70,
            opacity: logoOpacity,
            transform: `translateY(${logoY}px)`,
          }}
        />

        <h2
          style={{
            ...fadeUp(frame, 26),
            color: "#FFFFFF",
            fontSize: 72,
            fontWeight: 800,
            lineHeight: 1.1,
            margin: 0,
            maxWidth: 900,
          }}
        >
          Never Miss a Healthcare Job
        </h2>

        <div
          style={{
            ...fadeUp(frame, 34),
            color: "#8899AA",
            fontSize: 32,
            fontWeight: 600,
            lineHeight: 1.45,
            marginTop: 24,
          }}
        >
          Follow @jobbermed for weekly alerts
        </div>

        <div
          style={{
            ...fadeUp(frame, 44),
            alignItems: "center",
            display: "flex",
            flexDirection: "column",
            gap: 20,
            marginTop: 70,
            width: "100%",
          }}
        >
          <div
            style={{
              alignItems: "center",
              backgroundColor: "#00B4D8",
              borderRadius: 999,
              color: "#FFFFFF",
              display: "flex",
              fontSize: 28,
              fontWeight: 800,
              height: 84,
              justifyContent: "center",
              maxWidth: 760,
              padding: "0 42px",
              width: "100%",
            }}
          >
            Get Weekly Job Alerts
          </div>

          <div
            style={{
              alignItems: "center",
              backgroundColor: "transparent",
              border: "1px solid rgba(255, 255, 255, 0.72)",
              borderRadius: 999,
              color: "#FFFFFF",
              display: "flex",
              fontSize: 28,
              fontWeight: 800,
              height: 84,
              justifyContent: "center",
              maxWidth: 760,
              padding: "0 42px",
              width: "100%",
            }}
          >
            Browse Jobs at jobbermed.com
          </div>
        </div>
      </div>

      <div
        style={{
          ...fadeUp(frame, 58),
          bottom: 96,
          color: "#8899AA",
          fontSize: 24,
          fontWeight: 600,
          left: 0,
          lineHeight: 1.4,
          position: "absolute",
          right: 0,
          zIndex: 1,
        }}
      >
        New jobs every week. Free.
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
          zIndex: 1,
        }}
      >
        www.jobbermed.com
      </div>
    </AbsoluteFill>
  );
};
