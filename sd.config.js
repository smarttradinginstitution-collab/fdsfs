// sd.config.js
export default {
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/**/*.json'
  ],

  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables', // Using the default format
        options: {
          selector: ':root',
          outputReferences: false,
        }
      }]
    }
  }
};
