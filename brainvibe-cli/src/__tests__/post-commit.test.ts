import * as fs from 'fs';
import * as path from 'path';
import { simpleGit } from 'simple-git';
import { main } from '../hooks/post-commit';
import { jest } from '@jest/globals';

jest.mock('fs');
jest.mock('simple-git');

describe('post-commit hook', () => {
  const mockProjectPath = '/test/project';
  const mockConfig = {
    name: 'test-project',
    path: mockProjectPath,
    createdAt: '2024-01-01T00:00:00.000Z'
  };
  const mockCommit = {
    hash: 'abc123',
    message: 'Test commit',
    date: '2024-01-01T00:00:00.000Z',
    author_name: 'Test User'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    (fs.readFileSync as jest.Mock).mockImplementation((filePath) => {
      if (filePath.includes('config.json')) {
        return JSON.stringify(mockConfig);
      }
      if (filePath.includes('graph.json')) {
        return JSON.stringify({});
      }
      return '';
    });
    (fs.writeFileSync as jest.Mock).mockImplementation(() => {});
    (simpleGit as jest.Mock).mockReturnValue({
      log: jest.fn().mockResolvedValue({ latest: mockCommit })
    });
  });

  it('should update graph with commit info', async () => {
    await main();

    expect(fs.writeFileSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe', 'graph.json'),
      expect.stringContaining(mockCommit.hash)
    );
  });

  it('should throw error if project is not initialized', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    await expect(main()).rejects.toThrow('Project not initialized');
  });

  it('should throw error if no commit found', async () => {
    (simpleGit as jest.Mock).mockReturnValue({
      log: jest.fn().mockResolvedValue({ latest: null })
    });

    await expect(main()).rejects.toThrow('No commit found');
  });

  it('should handle existing graph data', async () => {
    const existingGraph = {
      commits: [
        {
          hash: 'def456',
          message: 'Previous commit',
          date: '2024-01-01T00:00:00.000Z',
          author: 'Previous User'
        }
      ]
    };
    (fs.readFileSync as jest.Mock).mockImplementation((filePath) => {
      if (filePath.includes('config.json')) {
        return JSON.stringify(mockConfig);
      }
      if (filePath.includes('graph.json')) {
        return JSON.stringify(existingGraph);
      }
      return '';
    });

    await main();

    expect(fs.writeFileSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe', 'graph.json'),
      expect.stringContaining(mockCommit.hash)
    );
  });
}); 