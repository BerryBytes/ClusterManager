
import palette from "./palette";

export default {
  typography: {
    fontFamily: ["comfortaa", "sans-serif"].join(","),
  },
  h1: {
    // color: palette.text.primary,
    fontWeight: 700,
    fontSize: "2.5rem", // 40px
    letterSpacing: "-0.24px",
    lineHeight: "1.2",   // 48px (40px * 1.2)
    fontFamily: 'comfortaa, sans-serif',
  }
  ,
  h2: {
    // color: palette.text.primary,
    fontWeight: 700,
    fontSize: "2.125rem", // 34px
    letterSpacing: "-0.24px",
    fontFamily: 'comfortaa, sans-serif', lineHeight: "1.25",   // 42.5px (34px * 1.25)

  },
  h3: {
    color: palette.text.primary,
    fontWeight: 700,
    fontSize: "1.75rem", // 28px
    letterSpacing: "-0.06px",
    lineHeight: "1.286", // 36px (28px * 1.286)
    fontFamily: 'comfortaa, sans-serif',
  },
  h4: {
    color: palette.text.primary,
    fontWeight: 700,
    fontSize: "1.5rem", // 24px
    letterSpacing: "-0.06px",
    lineHeight: "1.333", // 32px (24px * 1.333)
    fontFamily: 'comfortaa, sans-serif',
  },
  h5: {
    color: palette.text.primary,
    fontWeight: 700,
    fontSize: "1.25rem", // 20px
    letterSpacing: "-0.05px",
    lineHeight: "1.6",    // 32px (20px * 1.6)
    fontFamily: 'comfortaa, sans-serif',
  },
  h6: {
    color: palette.text.primary,
    fontWeight: 700,
    fontSize: "1.125rem", // 18px
    letterSpacing: "-0.05px",
    lineHeight: "1.333",  // 24px (18px * 1.333)
    fontFamily: 'comfortaa, sans-serif',
  },
  subtitle1: {
    color: palette.text.primary,
    // fontSize: "1rem",    // 16px
    // letterSpacing: "-0.05px",
    fontFamily: 'comfortaa, sans-serif', lineHeight: "1.5625", // 25px (16px * 1.5625)

  },
  subtitle2: {
    // color: palette.text.secondary,
    fontWeight: 400,
    fontSize: "0.875rem", // 14px
    letterSpacing: "-0.05px",
    lineHeight: "1.5",    // 21px (14px * 1.5)
    fontFamily: 'comfortaa, sans-serif',
  },
  body1: {
    color: palette.text.primary,
    fontSize: "0.875rem", // 14px
    letterSpacing: "-0.05px",
    lineHeight: "1.5",    // 21px (14px * 1.5)
    fontFamily: 'comfortaa, sans-serif',
  },
  body2: {
    // color: palette.text.primary,
    fontSize: "0.75rem",  // 12px
    letterSpacing: "-0.04px",
    lineHeight: "1.5",    // 18px (12px * 1.5)
    fontFamily: 'comfortaa, sans-serif',
  },
  button: {
    // color: palette.text.primary,
    letterSpacing: "-0.04px",
    lineHeight: "1.5",    // 18px (12px * 1.5)
    fontFamily: 'comfortaa, sans-serif',
    fontSize: "0.875rem", // 14px
  },
  caption: {
    // color: palette.text.secondary,
    fontSize: "0.875rem", // 14px
    letterSpacing: "0.33px",
    fontFamily: 'comfortaa, sans-serif',
    lineHeight: "1.2857", // 18px (14px * 1.2857)

  },
  overline: {
    // color: palette.text.secondary,
    fontSize: "0.875rem", // 14px
    fontWeight: 700,
    letterSpacing: "0",
    fontFamily: 'comfortaa, sans-serif'
  }
}
