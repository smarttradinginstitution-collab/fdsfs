export default {
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/border/**/*.json',
    'tokens/semantic/effect/**/*.json',
    'tokens/semantic/font/**/*.json',
    'tokens/semantic/size/**/*.json',
    'tokens/semantic/color/dark.json'
  ],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [
        {
          destination: 'tokens-dark.css',
          format: 'css/variables',
          options: {
            selector: '[data-theme="dark"]',
            outputReferences: true,
          },
          filter: (token) => token.filePath.startsWith('tokens/semantic/')
        }
      ]
    }
  }
};
