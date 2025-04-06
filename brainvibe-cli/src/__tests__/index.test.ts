import { Command } from 'commander';
import { program } from '../index';
import { jest } from '@jest/globals';

jest.mock('commander');

describe('CLI', () => {
  let mockCommand: jest.Mocked<Command>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockCommand = {
      name: jest.fn().mockReturnThis(),
      description: jest.fn().mockReturnThis(),
      version: jest.fn().mockReturnThis(),
      command: jest.fn().mockReturnThis(),
      option: jest.fn().mockReturnThis(),
      action: jest.fn().mockReturnThis(),
      parse: jest.fn()
    } as unknown as jest.Mocked<Command>;
    (Command as jest.Mock).mockReturnValue(mockCommand);
  });

  it('should set up CLI program', () => {
    program;

    expect(mockCommand.name).toHaveBeenCalledWith('brainvibe');
    expect(mockCommand.description).toHaveBeenCalledWith(
      'A command-line tool for tracking learning progress and visualizing your knowledge graph'
    );
    expect(mockCommand.version).toHaveBeenCalledWith('1.0.0');
  });

  it('should set up init command', () => {
    program;

    expect(mockCommand.command).toHaveBeenCalledWith('init');
    expect(mockCommand.option).toHaveBeenCalledWith(
      '-p, --path <path>',
      'Project path',
      expect.any(Function)
    );
    expect(mockCommand.option).toHaveBeenCalledWith(
      '-n, --name <name>',
      'Project name'
    );
  });

  it('should set up track command', () => {
    program;

    expect(mockCommand.command).toHaveBeenCalledWith('track');
    expect(mockCommand.option).toHaveBeenCalledWith(
      '-p, --path <path>',
      'Project path',
      expect.any(Function)
    );
  });

  it('should set up graph command', () => {
    program;

    expect(mockCommand.command).toHaveBeenCalledWith('graph');
    expect(mockCommand.option).toHaveBeenCalledWith(
      '-p, --path <path>',
      'Project path',
      expect.any(Function)
    );
  });

  it('should set up learn command', () => {
    program;

    expect(mockCommand.command).toHaveBeenCalledWith('learn <topic>');
    expect(mockCommand.option).toHaveBeenCalledWith(
      '-p, --path <path>',
      'Project path',
      expect.any(Function)
    );
  });
}); 