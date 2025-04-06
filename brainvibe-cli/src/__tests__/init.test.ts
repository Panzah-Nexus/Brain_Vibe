import * as fs from 'fs';
import * as path from 'path';
import { initProject } from '../commands/init';
import { jest } from '@jest/globals';

jest.mock('fs');
jest.mock('simple-git');
jest.mock('inquirer');

describe('initProject', () => {
  const mockProjectPath = '/test/project';
  const mockProjectName = 'test-project';

  beforeEach(() => {
    jest.clearAllMocks();
    (fs.existsSync as jest.Mock).mockReturnValue(false);
    (fs.mkdirSync as jest.Mock).mockImplementation(() => {});
    (fs.writeFileSync as jest.Mock).mockImplementation(() => {});
  });

  it('should initialize a new project', async () => {
    await initProject({ path: mockProjectPath, name: mockProjectName });

    expect(fs.mkdirSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe'),
      { recursive: true }
    );

    expect(fs.writeFileSync).toHaveBeenCalledWith(
      path.join(mockProjectPath, '.brainvibe', 'config.json'),
      expect.stringContaining(mockProjectName)
    );
  });

  it('should throw error if project is already initialized', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(true);

    await expect(initProject({ path: mockProjectPath })).rejects.toThrow(
      'Project is already initialized'
    );
  });

  it('should prompt for project name if not provided', async () => {
    const mockInquirer = require('inquirer');
    mockInquirer.prompt.mockResolvedValue({ name: mockProjectName });

    await initProject({ path: mockProjectPath });

    expect(mockInquirer.prompt).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({
          name: 'name',
          message: 'Enter project name:'
        })
      ])
    );
  });
}); 