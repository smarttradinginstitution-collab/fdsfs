// =============================================================================
// FILE: sd.config.js
// DESCRIZIONE: File di configurazione per Style Dictionary.
// Questo file definisce come i nostri file di token JSON vengono trasformati
// in file CSS utilizzabili nell'applicazione.
// =============================================================================

export default {
  // `source` è un array di percorsi che dice a Style Dictionary dove trovare
  // i file di definizione dei token. Includiamo sia i token di base che quelli semantici.
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/**/*.json'
  ],

  // `platforms` definisce i diversi output che vogliamo generare.
  // In questo caso, generiamo solo CSS.
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      // `files` è un array che ci permette di generare più file di output
      // dalla stessa fonte di token, applicando filtri diversi.
      files: [
        {
          // Unico file di output che contiene TUTTI i token (base e semantici).
          // I token semantici faranno riferimento a quelli di base.
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            // outputReferences: true farà in modo che i token semantici
            // vengano risolti in var(--base-*) invece che in valori grezzi.
            outputReferences: true,
          }
        }
      ]
    }
  }
};
