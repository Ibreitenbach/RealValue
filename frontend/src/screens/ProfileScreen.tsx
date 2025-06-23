// frontend/src/screens/ProfileScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView } from 'react-native';
// Import shared types for profile data - will be used more in next step
// import { SharedUserProfileData, SharedUserProfileUpdatePayload } from '../../../../shared/models/profile';

// Placeholder for API service - will be implemented and used in the next step
// import { fetchUserProfile, updateUserProfile } from '../services/profileService';

const ProfileScreen: React.FC = () => {
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // In the next step, this useEffect will fetch actual data
  useEffect(() => {
    // Placeholder: load initial data (e.g., from API)
    // For now, just setting some defaults for UI check
    setDisplayName('YourDisplayName');
    setBio('A short bio about yourself.');
  }, []);

  const handleSaveProfile = async () => {
    setIsLoading(true);
    setError(null);

    // const payload: SharedUserProfileUpdatePayload = {};
    // if (displayName) payload.display_name = displayName;
    // if (bio) payload.bio = bio;

    // Placeholder for actual API call
    console.log('Saving profile with:', { displayName, bio });
    try {
      // await updateUserProfile(payload);
      // Simulating API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      Alert.alert('Profile Saved', 'Your profile has been updated successfully.');
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile. Please try again.');
      Alert.alert('Error', 'Failed to save profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>My Profile</Text>

      {error && <Text style={styles.errorText}>{error}</Text>}

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Display Name</Text>
        <TextInput
          style={styles.input}
          value={displayName}
          onChangeText={setDisplayName}
          placeholder="Enter your display name"
          editable={!isLoading}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Bio</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={bio}
          onChangeText={setBio}
          placeholder="Tell us about yourself"
          multiline
          numberOfLines={4}
          editable={!isLoading}
        />
      </View>

      <Button
        title={isLoading ? 'Saving...' : 'Save Profile'}
        onPress={handleSaveProfile}
        disabled={isLoading}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    marginBottom: 5,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top', // For Android
  },
  errorText: {
    color: 'red',
    marginBottom: 10,
    textAlign: 'center',
  },
});

export default ProfileScreen;
