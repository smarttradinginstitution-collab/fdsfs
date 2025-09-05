// sd.config.js

export default {
  // Sorgente di tutti i token, sia base che semantici.
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/**/*.json'
  ],

  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [
        // === 1. File dei token di base (_base.css) ===
        // Contiene solo i valori primitivi, non deve essere usato direttamente nei componenti.
        {
          destination: '_base.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            outputReferences: false, // Emette i valori grezzi (es. #ffffff)
          },
          // Filtra per includere solo i token provenienti dalla cartella 'base'.
          filter: (token) => token.filePath.startsWith('tokens/base/')
        },
        // === 2. File dei token semantici (tokens.css) ===
        // Contiene i token contestuali che fanno riferimento ai token di base.
        {
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            outputReferences: true, // Emette i riferimenti (es. var(--base-color-white))
          },
          // Filtra per includere solo i token provenienti dalla cartella 'semantic'.
          filter: (token) => token.filePath.startsWith('tokens/semantic/')
        }
      ]
    }
  }
};
