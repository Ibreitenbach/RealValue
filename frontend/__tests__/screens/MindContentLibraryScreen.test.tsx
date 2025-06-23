// frontend/__tests__/screens/MindContentLibraryScreen.test.tsx
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Linking, Alert } from 'react-native';
import MindContentLibraryScreen from '../../src/screens/MindContentLibraryScreen';
import * as mindContentService from '../../src/services/mindContentService';
import { MindContent, MindContentCategory, MindContentType } from '../../src/types/mindContentTypes';

jest.mock('../../src/services/mindContentService');
const mockedMindContentService = mindContentService as jest.Mocked<typeof mindContentService>;

const mockNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
}));

jest.spyOn(Linking, 'openURL');
jest.spyOn(Linking, 'canOpenURL');
jest.spyOn(Alert, 'alert');


const mockCategories: MindContentCategory[] = [
  { id: 1, name: 'Mindfulness', description: 'Stay present.' },
  { id: 2, name: 'Stoicism', description: 'Ancient wisdom.' },
];

const mockContentItems: MindContent[] = [
  { id: 101, title: 'Mindful Breathing Exercise', description: 'A 5-min exercise.', url: 'http://example.com/mindful-breath', content_type: MindContentType.VIDEO, category_id: 1, author_name: 'Zen Master' },
  { id: 102, title: 'Meditations by Marcus Aurelius', description: 'Summary and key lessons.', url: 'http://example.com/marcus-aurelius', content_type: MindContentType.ARTICLE, category_id: 2, author_name: 'Book Summary Inc.' },
];

describe('MindContentLibraryScreen', () => {
  beforeEach(() => {
    mockedMindContentService.getMindContentCategories.mockClear();
    mockedMindContentService.getMindContent.mockClear();
    mockNavigate.mockClear();
    (Linking.openURL as jest.Mock).mockClear();
    (Linking.canOpenURL as jest.Mock).mockClear().mockResolvedValue(true); // Assume canOpenURL is true by default
    (Alert.alert as jest.Mock).mockClear();

    // Default successful mocks
    mockedMindContentService.getMindContentCategories.mockResolvedValue(mockCategories);
    mockedMindContentService.getMindContent.mockResolvedValue(mockContentItems);
  });

  it('renders loading state initially', () => {
    mockedMindContentService.getMindContentCategories.mockReturnValue(new Promise(() => {}));
    mockedMindContentService.getMindContent.mockReturnValue(new Promise(() => {}));
    const { getByText } = render(<MindContentLibraryScreen />);
    expect(getByText('Loading Content Library...')).toBeTruthy();
  });

  it('renders content items and categories after successful fetch', async () => {
    const { findByText } = render(<MindContentLibraryScreen />);
    expect(await findByText('Mindful Breathing Exercise')).toBeTruthy();
    expect(await findByText('Meditations by Marcus Aurelius')).toBeTruthy();
    // Check if category filter buttons are rendered
    expect(await findByText(mockCategories[0].name)).toBeTruthy();
    expect(await findByText(mockCategories[1].name)).toBeTruthy();
  });

  it('handles error when fetching categories', async () => {
    mockedMindContentService.getMindContentCategories.mockRejectedValueOnce(new Error('Category fetch failed'));
    const { findByText } = render(<MindContentLibraryScreen />);
    expect(await findByText('Error: Category fetch failed')).toBeTruthy();
  });

  it('handles error when fetching content', async () => {
    // Categories load fine, content fails
    mockedMindContentService.getMindContent.mockRejectedValueOnce(new Error('Content fetch failed'));
    const { findByText } = render(<MindContentLibraryScreen />);
    expect(await findByText('Error: Content fetch failed')).toBeTruthy();
  });

  it('filters content by category when a category button is pressed and applied', async () => {
    const { getByText, findByText } = render(<MindContentLibraryScreen />);
    await findByText('Mindful Breathing Exercise'); // Ensure initial load

    fireEvent.press(getByText(mockCategories[0].name)); // Click "Mindfulness" category
    fireEvent.press(getByText('Apply Search & Filters'));

    await waitFor(() => {
      expect(mockedMindContentService.getMindContent).toHaveBeenCalledWith(
        expect.objectContaining({ category_id: mockCategories[0].id })
      );
    });
  });

  it('filters content by search term when submitted', async () => {
    const { getByPlaceholderText, getByText, findByText } = render(<MindContentLibraryScreen />);
    await findByText('Mindful Breathing Exercise');

    fireEvent.changeText(getByPlaceholderText('Search title or description...'), 'Marcus');
    fireEvent.press(getByText('Apply Search & Filters'));

    await waitFor(() => {
      expect(mockedMindContentService.getMindContent).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'Marcus' })
      );
    });
  });

  it('opens content URL using Linking', async () => {
    const { findAllByText } = render(<MindContentLibraryScreen />);
    // Get all "Go to Content" buttons. This might need to be more specific if titles are similar
    const goToContentButtons = await findAllByText('Go to Content');
    fireEvent.press(goToContentButtons[0]); // Press first one

    expect(Linking.canOpenURL).toHaveBeenCalledWith(mockContentItems[0].url);
    expect(Linking.openURL).toHaveBeenCalledWith(mockContentItems[0].url);
  });

  it('shows alert if URL cannot be opened', async () => {
    (Linking.canOpenURL as jest.Mock).mockResolvedValueOnce(false);
    const { findAllByText } = render(<MindContentLibraryScreen />);
    const goToContentButtons = await findAllByText('Go to Content');
    fireEvent.press(goToContentButtons[0]);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith("Error", `Don't know how to open this URL: ${mockContentItems[0].url}`);
    });
  });

  it('navigates to MindContentForm when "Suggest New Content" is pressed', async () => {
    const { getByText, findByText } = render(<MindContentLibraryScreen />);
    await findByText('Mindful Breathing Exercise'); // Ensure screen is loaded

    fireEvent.press(getByText('Suggest New Content'));
    expect(mockNavigate).toHaveBeenCalledWith('MindContentForm', { mode: 'add' });
  });

  it('displays "no content found" message correctly', async () => {
    mockedMindContentService.getMindContent.mockResolvedValue([]); // Return empty content
    const { findByText } = render(<MindContentLibraryScreen />);
    expect(await findByText('No content found for the selected criteria.')).toBeTruthy();
  });

});
