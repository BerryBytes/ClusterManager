import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021
      },
    },
    rules: {
      // Possible Problems
      "no-duplicate-imports": "error",
      "no-unused-vars": "warn",
      "no-console": "warn",
      
      // Suggestions
      "curly": ["error", "multi-line"],
      "default-case": "warn",
      "eqeqeq": ["error", "always"],
      "no-eval": "error",
      "no-var": "error",
      "prefer-const": "warn",
      
      // Layout & Formatting
      "array-bracket-spacing": ["error", "never"],
      "block-spacing": "error",
      "brace-style": ["error", "1tbs"],
      "comma-dangle": ["error", "always-multiline"],
      "comma-spacing": ["error", { "before": false, "after": true }],
      "indent": ["error", 2],
      "quotes": ["error", "single"],
      "semi": ["error", "always"],
      
      // ES6
      "arrow-spacing": "error",
      "no-const-assign": "error",
      "prefer-template": "warn",
      "template-curly-spacing": ["error", "never"]
    },
    
    env: {
      browser: true,
      node: true,
      es2022: true
    }
  }
];