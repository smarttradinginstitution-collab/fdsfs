import StyleDictionary from 'style-dictionary';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import fs from 'fs/promises';

// ESM-friendly way to get __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Array of configuration files
const configs = [
  './sd.base.config.js',
  './sd.light.config.js',
  './sd.dark.config.js'
];

async function buildStyleDictionaryTokens() {
  console.log('Building CSS variables from tokens...');
  for (const configPath of configs) {
    const configModule = await import(resolve(__dirname, configPath));
    const sd = new StyleDictionary(configModule.default);
    await sd.buildAllPlatforms();
  }
}

async function createBreakpointMixins() {
  console.log('Creating SCSS breakpoint mixins...');
  try {
    const breakpointTokenPath = resolve(__dirname, 'tokens/base/layout/breakpoint.json');
    const data = await fs.readFile(breakpointTokenPath, 'utf8');
    const breakpoints = JSON.parse(data).base.layout.breakpoint;

    let scssContent = '// Do not edit directly, this file was auto-generated from breakpoint.json.\n\n';
    scssContent += '// Mobile-first media query mixins\n\n';

    for (const name in breakpoints) {
      const value = breakpoints[name].$value;
      scssContent += `@mixin mq-${name} {\n`;
      scssContent += `  @media (min-width: ${value}) {\n`;
      scssContent += `    @content;\n`;
      scssContent += `  }\n`;
      scssContent += `}\n\n`;
    }

    const output_path = resolve(__dirname, 'src/styles/_breakpoints.scss');
    await fs.writeFile(output_path, scssContent);
    console.log('Successfully created _breakpoints.scss');

  } catch (error) {
    console.error('Error creating breakpoint mixins:', error);
    process.exit(1);
  }
}

async function build() {
  await buildStyleDictionaryTokens();
  await createBreakpointMixins();
  console.log('\nToken build process complete.');
}

build();
