import * as fs from 'fs';
import * as path from 'path';
import chokidar from 'chokidar';
import { simpleGit } from 'simple-git';
import { trackChanges } from '../commands/track';
import { jest } from '@jest/globals';

jest.mock('fs');
jest.mock('chokidar');
jest.mock('simple-git');

describe('trackChanges', () => {
  const mockProjectPath = '/test/project';
  const mockConfig = {
    name: 'test-project',
    path: mockProjectPath,
    createdAt: '2024-01-01T00:00:00.000Z'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify(mockConfig));
    (chokidar.watch as jest.Mock).mockReturnValue({
      on: jest.fn()
    });
  });

  it('should start tracking changes', async () => {
    await trackChanges({ path: mockProjectPath });

    expect(chokidar.watch).toHaveBeenCalledWith(mockProjectPath, {
      ignored: expect.arrayContaining([
        /(^|[\/\\])\../,
        '**/node_modules/**',
        '**/.git/**',
        '**/.brainvibe/**'
      ]),
      persistent: true
    });
  });

  it('should throw error if project is not initialized', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    await expect(trackChanges({ path: mockProjectPath })).rejects.toThrow(
      'Project not initialized'
    );
  });

  it('should handle file changes', async () => {
    const mockWatcher = {
      on: jest.fn()
    };
    (chokidar.watch as jest.Mock).mockReturnValue(mockWatcher);

    await trackChanges({ path: mockProjectPath });

    expect(mockWatcher.on).toHaveBeenCalledWith('add', expect.any(Function));
    expect(mockWatcher.on).toHaveBeenCalledWith('change', expect.any(Function));
    expect(mockWatcher.on).toHaveBeenCalledWith('unlink', expect.any(Function));
  });
}); 