// frontend/__tests__/screens/PracticeChallengesScreen.test.tsx
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import PracticeChallengesScreen from '../../src/screens/PracticeChallengesScreen';
import * as challengeService from '../../src/services/challengeService';
import { PracticeChallengeTemplate, ChallengeType, DifficultyLevel } from '../../src/types/challengeTypes';

// Mock challengeService
jest.mock('../../src/services/challengeService');
const mockedChallengeService = challengeService as jest.Mocked<typeof challengeService>;

// Mock navigation
const mockNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
}));

const mockTemplates: PracticeChallengeTemplate[] = [
  { id: 1, title: 'Easy Challenge', description: 'An easy one.', challenge_type: ChallengeType.TEXT_RESPONSE, difficulty: DifficultyLevel.EASY, is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: 1 },
  { id: 2, title: 'Medium Challenge', description: 'A bit harder.', challenge_type: ChallengeType.PHOTO_UPLOAD, difficulty: DifficultyLevel.MEDIUM, is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: null },
  { id: 3, title: 'Hard Challenge', description: 'Tough one.', challenge_type: ChallengeType.CHECKBOX_COMPLETION, difficulty: DifficultyLevel.HARD, is_active: true, created_at: 'date', updated_at: 'date', associated_skill_id: 2 },
];

describe('PracticeChallengesScreen', () => {
  beforeEach(() => {
    mockedChallengeService.getChallengeTemplates.mockClear();
    mockNavigate.mockClear();
  });

  it('renders loading state initially', () => {
    mockedChallengeService.getChallengeTemplates.mockReturnValue(new Promise(() => {})); // Never resolves
    const { getByText } = render(<PracticeChallengesScreen />);
    expect(getByText('Loading challenges...')).toBeTruthy();
  });

  it('renders challenges after successful fetch', async () => {
    mockedChallengeService.getChallengeTemplates.mockResolvedValue(mockTemplates);
    const { findByText } = render(<PracticeChallengesScreen />);
    expect(await findByText('Easy Challenge')).toBeTruthy();
    expect(await findByText('Medium Challenge')).toBeTruthy();
    expect(await findByText('Hard Challenge')).toBeTruthy();
  });

  it('renders error message on fetch failure', async () => {
    mockedChallengeService.getChallengeTemplates.mockRejectedValue(new Error('Failed to fetch'));
    const { findByText } = render(<PracticeChallengesScreen />);
    expect(await findByText('Error: Failed to fetch')).toBeTruthy();
  });

  it('renders "no challenges found" when list is empty', async () => {
    mockedChallengeService.getChallengeTemplates.mockResolvedValue([]);
    const { findByText } = render(<PracticeChallengesScreen />);
    expect(await findByText('No challenges found for the selected filters.')).toBeTruthy();
  });

  it('calls getChallengeTemplates with difficulty filter when "Easy" button is pressed and applied', async () => {
    mockedChallengeService.getChallengeTemplates.mockResolvedValue([]); // Initial load
    const { getByText, findByText } = render(<PracticeChallengesScreen />);

    await findByText("Practice Challenges"); // Ensure initial load is processed

    fireEvent.press(getByText('Easy'));
    fireEvent.press(getByText('Apply Filters'));

    await waitFor(() => {
      expect(mockedChallengeService.getChallengeTemplates).toHaveBeenCalledWith({ difficulty: DifficultyLevel.EASY });
    });
  });

  it('navigates to ChallengeAttempt screen when "Attempt Challenge" is pressed', async () => {
    mockedChallengeService.getChallengeTemplates.mockResolvedValue([mockTemplates[0]]);
    const { findByText } = render(<PracticeChallengesScreen />);

    const attemptButton = await findByText('Attempt Challenge');
    fireEvent.press(attemptButton);

    expect(mockNavigate).toHaveBeenCalledWith('ChallengeAttempt', { challengeId: mockTemplates[0].id });
  });

  it('allows retrying fetch on error', async () => {
    mockedChallengeService.getChallengeTemplates.mockRejectedValueOnce(new Error('Fetch Error'));
    const { findByText, getByText } = render(<PracticeChallengesScreen />);

    expect(await findByText('Error: Fetch Error')).toBeTruthy();

    mockedChallengeService.getChallengeTemplates.mockResolvedValueOnce([mockTemplates[0]]); // Setup for successful retry
    fireEvent.press(getByText('Retry'));

    expect(await findByText(mockTemplates[0].title)).toBeTruthy();
    expect(mockedChallengeService.getChallengeTemplates).toHaveBeenCalledTimes(2);
  });

});
