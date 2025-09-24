export default {
  source: [
    'tokens/base/**/*.json'
  ],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [
        {
          destination: '_base.css',
          format: 'css/variables',
          options: { selector: ':root', outputReferences: false }
        }
      ]
    }
  }
};
