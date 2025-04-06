#!/usr/bin/env node

import { Command } from 'commander';
import { initProject } from './commands/init';
import { trackChanges } from './commands/track';
import { showGraph } from './commands/graph';
import { markLearned } from './commands/learn';

const program = new Command();

program
  .name('brainvibe')
  .description('A command-line tool for tracking learning progress and visualizing your knowledge graph')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize a new BrainVibe project')
  .option('-p, --path <path>', 'Project path', process.cwd())
  .option('-n, --name <name>', 'Project name')
  .action(async (options) => {
    try {
      await initProject(options);
    } catch (error) {
      if (error instanceof Error) {
        console.error('Error:', error.message);
      } else {
        console.error('Error:', String(error));
      }
      process.exit(1);
    }
  });

program
  .command('track')
  .description('Start tracking changes in your project')
  .option('-p, --path <path>', 'Project path', process.cwd())
  .option('-i, --interval <ms>', 'Commit interval in milliseconds', '120000')
  .option('--ignore-file <file>', 'Custom ignore file (default: .brainvibeignore)')
  .action(async (options) => {
    try {
      // Convert interval string to number
      if (options.interval) {
        options.interval = parseInt(options.interval, 10);
      }
      await trackChanges(options);
    } catch (error) {
      if (error instanceof Error) {
        console.error('Error:', error.message);
      } else {
        console.error('Error:', String(error));
      }
      process.exit(1);
    }
  });

program
  .command('graph')
  .description('Display your learning graph')
  .option('-p, --path <path>', 'Project path', process.cwd())
  .action(async (options) => {
    try {
      await showGraph(options);
    } catch (error) {
      if (error instanceof Error) {
        console.error('Error:', error.message);
      } else {
        console.error('Error:', String(error));
      }
      process.exit(1);
    }
  });

program
  .command('learn <topic>')
  .description('Mark a topic as learned')
  .option('-p, --path <path>', 'Project path', process.cwd())
  .action(async (topic, options) => {
    try {
      await markLearned(topic, options);
    } catch (error) {
      if (error instanceof Error) {
        console.error('Error:', error.message);
      } else {
        console.error('Error:', String(error));
      }
      process.exit(1);
    }
  });

program.parse(process.argv); 