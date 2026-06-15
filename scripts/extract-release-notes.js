#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

const releaseNotePath = path.resolve('RELEASE_NOTE.md');
const outputPath = path.resolve('LATEST_RELEASE_NOTE.md');

try {
    const content = fs.readFileSync(releaseNotePath, 'utf-8');

    // Split by horizontal rules (---) or the next main header (# Release)
    // We want everything before the first '---' or before the second '# Release'
    const lines = content.split('\n');
    let latestNotes = [];
    let headerCount = 0;

    for (const line of lines) {
        if (line.trim().startsWith('# Release')) {
            headerCount++;
            if (headerCount > 1) break;
        }
        if (line.trim() === '---' && headerCount === 1) break;

        latestNotes.push(line);
    }

    fs.writeFileSync(outputPath, latestNotes.join('\n').trim());
    console.log('Successfully extracted latest release notes to LATEST_RELEASE_NOTE.md');
} catch (error) {
    console.error('Error extracting release notes:', error.message);
    process.exit(1);
}
