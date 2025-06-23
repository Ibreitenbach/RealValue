// frontend/__tests__/screens/ChallengeAttemptScreen.test.tsx
import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import ChallengeAttemptScreen from '../../src/screens/ChallengeAttemptScreen';
import * as challengeService from '../../src/services/challengeService';
import { PracticeChallengeTemplate, ChallengeType, DifficultyLevel, UserChallengeCompletion, CompletionStatus } from '../../src/types/challengeTypes';
import { Alert } from 'react-native';

jest.mock('../../src/services/challengeService');
const mockedChallengeService = challengeService as jest.Mocked<typeof challengeService>;

const mockNavigate = jest.fn();
const mockGoBack = jest.fn();
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
    goBack: mockGoBack,
  }),
  useRoute: () => ({
    params: {
      challengeId: 1, // Default mock challengeId
    },
  }),
}));

jest.spyOn(Alert, 'alert');

const mockTextChallenge: PracticeChallengeTemplate = {
  id: 1, title: 'Text Challenge', description: 'Respond with text.',
  challenge_type: ChallengeType.TEXT_RESPONSE, difficulty: DifficultyLevel.EASY,
  is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: null,
};

const mockCheckboxChallenge: PracticeChallengeTemplate = {
  id: 2, title: 'Checkbox Challenge', description: 'Tick the box.',
  challenge_type: ChallengeType.CHECKBOX_COMPLETION, difficulty: DifficultyLevel.MEDIUM,
  is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: null,
};

const mockPhotoChallenge: PracticeChallengeTemplate = {
  id: 3, title: 'Photo Challenge', description: 'Upload a photo (simulated).',
  challenge_type: ChallengeType.PHOTO_UPLOAD, difficulty: DifficultyLevel.HARD,
  is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: null,
};

const mockSubmissionResponse: UserChallengeCompletion = {
  id: 1, user_id: 1, challenge_template_id: 1, status: CompletionStatus.COMPLETED,
  completed_at: 'date', user_response: 'Test response',
};

describe('ChallengeAttemptScreen', () => {
  beforeEach(() => {
    mockedChallengeService.getChallengeTemplateById.mockClear();
    mockedChallengeService.submitChallengeCompletion.mockClear();
    mockNavigate.mockClear();
    mockGoBack.mockClear();
    (Alert.alert as jest.Mock).mockClear();
  });

  it('renders loading state initially', () => {
    mockedChallengeService.getChallengeTemplateById.mockReturnValue(new Promise(() => {}));
    const { getByText } = render(<ChallengeAttemptScreen />);
    expect(getByText('Loading challenge details...')).toBeTruthy();
  });

  it('renders challenge details and text input for TEXT_RESPONSE type', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockTextChallenge);
    const { findByText, getByPlaceholderText } = render(<ChallengeAttemptScreen />);
    expect(await findByText('Text Challenge')).toBeTruthy();
    expect(getByPlaceholderText('Enter your response')).toBeTruthy();
  });

  it('renders info text for PHOTO_UPLOAD type', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockPhotoChallenge);
    const { findByText } = render(<ChallengeAttemptScreen />);
    expect(await findByText('Photo Challenge')).toBeTruthy();
    expect(findByText(/This challenge involves a photo upload/)).toBeTruthy();
  });

  it('renders checkbox UI for CHECKBOX_COMPLETION type', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockCheckboxChallenge);
    const { findByText, getByText } = render(<ChallengeAttemptScreen />);
    expect(await findByText('Checkbox Challenge')).toBeTruthy();
    expect(getByText('Mark as completed:')).toBeTruthy();
    expect(getByText(/Not Completed \(Mark\)/)).toBeTruthy(); // Initial state of button
  });

  it('submits text response successfully', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockTextChallenge);
    mockedChallengeService.submitChallengeCompletion.mockResolvedValue(mockSubmissionResponse);
    const { findByText, getByPlaceholderText, getByText: getByTextLocal } = render(<ChallengeAttemptScreen />);

    await findByText('Text Challenge'); // Wait for load
    fireEvent.changeText(getByPlaceholderText('Enter your response'), 'My test answer');
    fireEvent.press(getByTextLocal('Submit Completion'));

    await waitFor(() => {
      expect(mockedChallengeService.submitChallengeCompletion).toHaveBeenCalledWith({
        challenge_template_id: mockTextChallenge.id,
        user_response: 'My test answer',
      });
    });
    expect(Alert.alert).toHaveBeenCalledWith("Success", "Challenge completion submitted!");
    expect(mockGoBack).toHaveBeenCalled();
  });

  it('requires text input for text response challenge', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockTextChallenge);
    const { findByText, getByText: getByTextLocal } = render(<ChallengeAttemptScreen />);

    await findByText('Text Challenge');
    fireEvent.press(getByTextLocal('Submit Completion'));

    expect(Alert.alert).toHaveBeenCalledWith("Input Required", "Please enter your response.");
    expect(mockedChallengeService.submitChallengeCompletion).not.toHaveBeenCalled();
  });

  it('submits checkbox response successfully', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockCheckboxChallenge);
    mockedChallengeService.submitChallengeCompletion.mockResolvedValue(mockSubmissionResponse);
    const { findByText, getByText: getByTextLocal } = render(<ChallengeAttemptScreen />);

    await findByText('Checkbox Challenge');
    // Simulate clicking the button to toggle checkbox state
    fireEvent.press(getByTextLocal(/Not Completed \(Mark\)/)); // Mark as completed

    // Use act for state update causing re-render before pressing submit
    await act(async () => {
      fireEvent.press(getByTextLocal('Submit Completion'));
    });

    await waitFor(() => {
        expect(mockedChallengeService.submitChallengeCompletion).toHaveBeenCalledWith({
          challenge_template_id: mockCheckboxChallenge.id,
          user_response: 'Completed',
        });
    });
    expect(Alert.alert).toHaveBeenCalledWith("Success", "Challenge completion submitted!");
    expect(mockGoBack).toHaveBeenCalled();
  });

  it('handles submission error', async () => {
    mockedChallengeService.getChallengeTemplateById.mockResolvedValue(mockTextChallenge);
    mockedChallengeService.submitChallengeCompletion.mockRejectedValue(new Error('Submission Failed'));
    const { findByText, getByPlaceholderText, getByText: getByTextLocal } = render(<ChallengeAttemptScreen />);

    await findByText('Text Challenge');
    fireEvent.changeText(getByPlaceholderText('Enter your response'), 'Some answer');
    fireEvent.press(getByTextLocal('Submit Completion'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith("Error", "Submission Failed");
    });
  });

});
