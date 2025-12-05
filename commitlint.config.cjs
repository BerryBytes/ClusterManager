module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
        'type-enum': [2, 'always', [
            'feat',     // A new feature
            'fix',      // A bug fix
            'docs',     // Documentation only changes
            'style',    // Changes that do not affect code meaning
            'refactor', // A code change that neither fixes a bug nor adds a feature
            'perf',     // A code change that improves performance
            'test',     // Adding missing tests or correcting existing tests
            'build',    // Build system or external dependencies
            'ci',       // CI configuration changes
            'chore',    // Other changes that don't modify src or test files
            'revert',   // Reverts a previous commit
        ]],
        'type-case': [2, 'always', 'lowerCase'],
        'type-empty': [2, 'never'],
        'scope-case': [2, 'always', 'lowerCase'],
        'subject-empty': [2, 'never'],
        'subject-full-stop': [2, 'never', '.'],
        'header-max-length': [2, 'always', 72],
    },
};
