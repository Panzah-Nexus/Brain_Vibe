import * as fs from 'fs';
import * as path from 'path';
import { simpleGit } from 'simple-git';
import { showGraph } from '../commands/graph';

jest.mock('fs');
jest.mock('simple-git');

describe('showGraph', () => {
  const mockProjectPath = '/test/project';
  const mockConfig = {
    name: 'test-project',
    path: mockProjectPath,
    createdAt: '2024-01-01T00:00:00.000Z'
  };
  const mockGraph = {
    'topic-1': { progress: 50, lastUpdated: '2024-01-01T00:00:00.000Z' },
    'topic-2': { progress: 100, lastUpdated: '2024-01-02T00:00:00.000Z' }
  };
  const mockCommits = [
    {
      hash: 'abc123',
      message: 'Initial commit',
      date: '2024-01-01T00:00:00.000Z',
      author_name: 'Test User'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    (fs.readFileSync as jest.Mock).mockImplementation((filePath) => {
      if (filePath.includes('config.json')) {
        return JSON.stringify(mockConfig);
      }
      if (filePath.includes('graph.json')) {
        return JSON.stringify(mockGraph);
      }
      return '';
    });
    (simpleGit as jest.Mock).mockReturnValue({
      log: jest.fn().mockResolvedValue({ all: mockCommits })
    });
  });

  it('should display learning graph', async () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    await showGraph({ path: mockProjectPath });

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Learning Graph for "test-project"')
    );
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('topic-1: 50% complete')
    );
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('topic-2: 100% complete')
    );

    consoleSpy.mockRestore();
  });

  it('should throw error if project is not initialized', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    await expect(showGraph({ path: mockProjectPath })).rejects.toThrow(
      'Project not initialized'
    );
  });

  it('should handle missing graph file', async () => {
    (fs.existsSync as jest.Mock).mockImplementation((filePath) => {
      if (filePath.includes('graph.json')) {
        return false;
      }
      return true;
    });

    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    await showGraph({ path: mockProjectPath });

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Learning Graph for "test-project"')
    );

    consoleSpy.mockRestore();
  });
}); 