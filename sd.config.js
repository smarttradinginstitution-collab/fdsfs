import StyleDictionary from 'style-dictionary';

/**
 * Custom format per generare le Custom Media Queries.
 * Itera sui token di breakpoint e crea una regola @custom-media per ognuno.
 * Esempio di output: @custom-media --media-md (max-width: 768px);
 */
StyleDictionary.registerFormat({
  name: 'css/custom-media',
  format: function({ allTokens }) {
    return allTokens
      .map(prop => {
        // Assumiamo che i token dei breakpoint abbiano una struttura come:
        // base.layout.breakpoint.md
        const name = prop.path.slice(3).join('-'); // es. md
        return `@custom-media --media-${name} (max-width: ${prop.$value});`;
      })
      .join('\n');
  },
});


export default {
  // Sorgente di tutti i token, sia base che semantici.
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/**/*.json'
  ],

  platforms: {
    // Piattaforma esistente per generare le variabili CSS
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [
        {
          destination: '_base.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            outputReferences: false,
          },
          filter: (token) => token.filePath.startsWith('tokens/base/')
        },
        {
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            outputReferences: true,
          },
          filter: (token) => token.filePath.startsWith('tokens/semantic/')
        }
      ]
    },
    // Nuova piattaforma per generare le Custom Media Queries
    customMedia: {
        transformGroup: 'css',
        buildPath: 'src/styles/',
        files: [{
            destination: '_breakpoints.css',
            format: 'css/custom-media',
            // Filtra per includere solo i token dei breakpoint
            filter: (token) =>
              token.attributes.category === 'base' &&
              token.attributes.type === 'layout' &&
              token.attributes.item === 'breakpoint',
        }]
    }
  }
};
