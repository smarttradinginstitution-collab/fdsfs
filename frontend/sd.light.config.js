export default {
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/border/**/*.json',
    'tokens/semantic/effect/**/*.json',
    'tokens/semantic/font/**/*.json',
    'tokens/semantic/size/**/*.json',
    'tokens/semantic/color/light.json'
  ],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [
        {
          destination: 'tokens-light.css',
          format: 'css/variables',
          options: { selector: ':root', outputReferences: true },
          filter: (token) => token.filePath.endsWith('light.json')
        }
      ]
    }
  }
};
