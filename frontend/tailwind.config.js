var config = {
    darkMode: ["class"],
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        container: {
            center: true,
            padding: "1.5rem",
            screens: {
                "2xl": "1440px",
            },
        },
        extend: {
            colors: {
                background: "#F8FAFC",
                surface: "#FFFFFF",
                border: "#E2E8F0",
                primary: "#2563EB",
                "primary-dark": "#1D4ED8",
                success: "#16A34A",
                warning: "#F59E0B",
                danger: "#DC2626",
                "text-primary": "#0F172A",
                "text-secondary": "#475569",
                muted: "#64748B",
            },
            borderRadius: {
                xl: "0.75rem",
                "2xl": "1rem",
            },
            boxShadow: {
                soft: "0 8px 30px rgba(15, 23, 42, 0.06)",
            },
            keyframes: {
                "accordion-down": {
                    from: { height: "0" },
                    to: { height: "var(--radix-accordion-content-height)" },
                },
                "accordion-up": {
                    from: { height: "var(--radix-accordion-content-height)" },
                    to: { height: "0" },
                },
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
            },
        },
    },
    plugins: [],
};
export default config;
