// frontend/__tests__/screens/MindContentFormScreen.test.tsx
import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Alert } from 'react-native';
import MindContentFormScreen from '../../src/screens/MindContentFormScreen';
import * as mindContentService from '../../src/services/mindContentService';
import { MindContent, MindContentCategory, MindContentType, NewMindContentData } from '../../src/types/mindContentTypes';

jest.mock('../../src/services/mindContentService');
const mockedMindContentService = mindContentService as jest.Mocked<typeof mindContentService>;

const mockNavigate = jest.fn();
const mockGoBack = jest.fn();
let mockRouteParams: any = { mode: 'add', contentId: undefined };

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
    goBack: mockGoBack,
  }),
  useRoute: () => ({
    params: mockRouteParams,
  }),
}));

// Mock Picker
jest.mock('@react-native-picker/picker', () => ({
  Picker: (props: any) => {
    // Simulate Picker behavior for testing: onChange gets called with selected value
    // Children are Picker.Item, so we can map them to simulate selection
    const { selectedValue, onValueChange, children, ...rest } = props;
    return (
      <View {...rest} testID="mock-picker">
        {React.Children.map(children, (child: any) => (
          <Button
            title={child.props.label}
            onPress={() => onValueChange(child.props.value, 0)} // Pass value and index
            testID={`picker-item-${child.props.value}`}
          />
        ))}
      </View>
    );
  }
}));


jest.spyOn(Alert, 'alert');

const mockCategories: MindContentCategory[] = [
  { id: 1, name: 'Category 1' },
  { id: 2, name: 'Category 2' },
];

const mockExistingContent: MindContent = {
  id: 123, title: 'Existing Title', description: 'Existing Desc', url: 'http://example.com/existing',
  content_type: MindContentType.VIDEO, category_id: 1, author_name: 'Old Author', duration_minutes: 30,
};

describe('MindContentFormScreen', () => {
  beforeEach(() => {
    mockedMindContentService.getMindContentCategories.mockClear();
    mockedMindContentService.getMindContentById.mockClear();
    mockedMindContentService.addMindContent.mockClear();
    mockedMindContentService.updateMindContent.mockClear();
    mockNavigate.mockClear();
    mockGoBack.mockClear();
    (Alert.alert as jest.Mock).mockClear();
    mockRouteParams = { mode: 'add', contentId: undefined }; // Reset route params
    mockedMindContentService.getMindContentCategories.mockResolvedValue(mockCategories); // Default mock for categories
  });

  it('renders correctly in "add" mode and loads categories', async () => {
    const { getByText, getByPlaceholderText, findAllByText } = render(<MindContentFormScreen />);
    expect(await findByText('Suggest New Content')).toBeTruthy();
    expect(getByPlaceholderText('Enter title')).toBeTruthy();
    // Check if categories are loaded into picker (mocked)
    expect(await findAllByText('Category 1')).toHaveLength(1); // Each category name appears once as a button title in mock
  });

  it('renders correctly in "edit" mode and loads existing content data', async () => {
    mockRouteParams = { mode: 'edit', contentId: mockExistingContent.id };
    mockedMindContentService.getMindContentById.mockResolvedValue(mockExistingContent);
    const { findByText, getByDisplayValue } = render(<MindContentFormScreen />);

    expect(await findByText('Edit Content')).toBeTruthy();
    expect(await getByDisplayValue('Existing Title')).toBeTruthy();
    expect(await getByDisplayValue('Existing Desc')).toBeTruthy();
    expect(await getByDisplayValue('http://example.com/existing')).toBeTruthy();
    expect(await getByDisplayValue('Old Author')).toBeTruthy();
    expect(await getByDisplayValue('30')).toBeTruthy(); // duration_minutes
    // Check if correct category and type are selected (harder to check with mock picker directly by selectedValue)
  });

  it('validates required fields on submit', async () => {
    const { getByText } = render(<MindContentFormScreen />);
    await waitFor(() => expect(getByText('Add Content')).toBeTruthy()); // Wait for categories to load potentially

    fireEvent.press(getByText('Add Content'));
    expect(Alert.alert).toHaveBeenCalledWith('Validation Error', 'Title, Description, and URL are required.');
    expect(mockedMindContentService.addMindContent).not.toHaveBeenCalled();
  });

  it('submits new content successfully in "add" mode', async () => {
    const { getByText, getByPlaceholderText, findAllByTestId } = render(<MindContentFormScreen />);
    await waitFor(() => expect(getByText('Add Content')).toBeTruthy());

    fireEvent.changeText(getByPlaceholderText('Enter title'), 'New Test Content');
    fireEvent.changeText(getByPlaceholderText('Enter description'), 'A great piece of content.');
    fireEvent.changeText(getByPlaceholderText('https://example.com'), 'http://new.example.com');

    // Simulate Picker selection for category (assuming categories loaded)
    const categoryPickerItems = await findAllByTestId(/picker-item-/); // Find all category items
    fireEvent.press(categoryPickerItems.find(item => item.props.testID === `picker-item-${mockCategories[0].id}`)!);


    mockedMindContentService.addMindContent.mockResolvedValueOnce({ ...mockExistingContent, id: 1 }); // Dummy response

    await act(async () => {
      fireEvent.press(getByText('Add Content'));
    });

    await waitFor(() => {
      expect(mockedMindContentService.addMindContent).toHaveBeenCalledWith(expect.objectContaining({
        title: 'New Test Content',
        description: 'A great piece of content.',
        url: 'http://new.example.com',
        category_id: mockCategories[0].id, // Check if category was selected
      }));
    });
    expect(Alert.alert).toHaveBeenCalledWith('Success', 'Content added successfully!');
    expect(mockGoBack).toHaveBeenCalled();
  });

  it('submits updated content successfully in "edit" mode', async () => {
    mockRouteParams = { mode: 'edit', contentId: mockExistingContent.id };
    mockedMindContentService.getMindContentById.mockResolvedValue(mockExistingContent);
    mockedMindContentService.updateMindContent.mockResolvedValueOnce(mockExistingContent);

    const { getByText, getByDisplayValue } = render(<MindContentFormScreen />);
    await waitFor(() => expect(getByDisplayValue('Existing Title')).toBeTruthy()); // Wait for form to populate

    fireEvent.changeText(getByDisplayValue('Existing Title'), 'Updated Super Title');

    await act(async () => {
       fireEvent.press(getByText('Update Content'));
    });

    await waitFor(() => {
      expect(mockedMindContentService.updateMindContent).toHaveBeenCalledWith(
        mockExistingContent.id,
        expect.objectContaining({ title: 'Updated Super Title' })
      );
    });
    expect(Alert.alert).toHaveBeenCalledWith('Success', 'Content updated successfully!');
    expect(mockGoBack).toHaveBeenCalled();
  });

  it('handles API error on submission', async () => {
    const { getByText, getByPlaceholderText, findAllByTestId } = render(<MindContentFormScreen />);
    await waitFor(() => expect(getByText('Add Content')).toBeTruthy());

    fireEvent.changeText(getByPlaceholderText('Enter title'), 'Error Test');
    fireEvent.changeText(getByPlaceholderText('Enter description'), 'This will fail.');
    fireEvent.changeText(getByPlaceholderText('https://example.com'), 'http://fail.example.com');
    const categoryPickerItems = await findAllByTestId(/picker-item-/);
    fireEvent.press(categoryPickerItems.find(item => item.props.testID === `picker-item-${mockCategories[0].id}`)!);


    mockedMindContentService.addMindContent.mockRejectedValueOnce(new Error('API Server Error'));

    await act(async () => {
        fireEvent.press(getByText('Add Content'));
    });

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', 'API Server Error');
    });
    expect(mockGoBack).not.toHaveBeenCalled();
  });

});
