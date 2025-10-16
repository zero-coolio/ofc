// fe/tailwind.config.js
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                oft: {
                    teal: "#0f766e",
                    light: "#c8eee9",
                    pale: "#e9f7f5",
                },
            },
        },
    },
    plugins: [],
};
