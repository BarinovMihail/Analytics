export default {
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            colors: {
                ink: "#0f172a",
                canvas: "#f4f7fb",
                panel: "#ffffff",
                line: "#d9e2ec",
                accent: {
                    DEFAULT: "#0f766e",
                    soft: "#ccfbf1",
                    dark: "#115e59",
                },
            },
            boxShadow: {
                panel: "0 10px 30px rgba(15, 23, 42, 0.08)",
            },
            fontFamily: {
                sans: ["Manrope", "Segoe UI", "sans-serif"],
            },
            backgroundImage: {
                grid: "linear-gradient(rgba(15, 118, 110, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(15, 118, 110, 0.03) 1px, transparent 1px)",
            },
        },
    },
    plugins: [],
};
