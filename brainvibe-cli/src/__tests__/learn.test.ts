import * as fs from 'fs';
import * as path from 'path';
import inquirer from 'inquirer';
import { markLearned } from '../commands/learn';
import { jest } from '@jest/globals';

jest.mock('fs');
jest.mock('inquirer');

describe('markLearned', () => {
  const mockProjectPath = '/test/project';
  const mockConfig = {
    name: 'test-project',
    path: mockProjectPath,
    createdAt: '2024-01-01T00:00:00.000Z'
  };
  const mockTopic = 'test-topic';
  const mockProgress = 75;

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
    (inquirer.prompt as jest.Mock).mockResolvedValue({ progress: mockProgress });
  });

  it('should mark topic as learned', async () => {
    await markLearned(mockTopic, { path: mockProjectPath });

    expect(inquirer.prompt).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({
          type: 'number',
          name: 'progress',
          message: expect.stringContaining(mockTopic)
        })
      ])
    );

    expect(fs.writeFileSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe', 'graph.json'),
      expect.stringContaining(mockTopic)
    );
  });

  it('should throw error if project is not initialized', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    await expect(markLearned(mockTopic, { path: mockProjectPath })).rejects.toThrow(
      'Project not initialized'
    );
  });

  it('should update existing topic progress', async () => {
    const existingGraph = {
      [mockTopic]: { progress: 50, lastUpdated: '2024-01-01T00:00:00.000Z' }
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

    await markLearned(mockTopic, { path: mockProjectPath });

    expect(fs.writeFileSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe', 'graph.json'),
      expect.stringContaining(mockProgress.toString())
    );
  });
}); 