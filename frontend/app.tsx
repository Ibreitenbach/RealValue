// frontend/app.tsx
import "react-native-gesture-handler"; // Required for react-navigation
import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { Button, View, Text } from "react-native"; // For the temporary navigation button

import HealthCheckScreen from "./src/screens/HealthCheckScreen";
import PracticeChallengesScreen from "./src/screens/PracticeChallengesScreen";
import ChallengeAttemptScreen from "./src/screens/ChallengeAttemptScreen";
import MyCompletionsScreen from "./src/screens/MyCompletionsScreen";
import MindContentLibraryScreen from "./src/screens/MindContentLibraryScreen"; // Added
import MindContentFormScreen from "./src/screens/MindContentFormScreen"; // Added

// Define param types for each screen
export type RootStackParamList = {
  MainHome: undefined; // A new initial screen that can navigate
  HealthCheck: undefined;
  PracticeChallenges: undefined;
  ChallengeAttempt: { challengeId: number };
  MyCompletions: undefined;
  MindContentLibrary: undefined;
  MindContentForm: { mode: 'add' } | { mode: 'edit'; contentId: number };
};

const Stack = createStackNavigator<RootStackParamList>();

// Temporary Home Screen to provide navigation options
const MainHomeScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <Text style={{ fontSize: 20, marginBottom: 20 }}>RealValue App Home</Text>
      <Button
        title="Go to Health Check"
        onPress={() => navigation.navigate("HealthCheck")}
      />
      <View style={{ marginVertical: 10 }} />
      <Button
        title="Browse Practice Challenges"
        onPress={() => navigation.navigate("PracticeChallenges")}
      />
      <View style={{ marginVertical: 10 }} />
      <Button
        title="View My Completions"
        onPress={() => navigation.navigate("MyCompletions")}
      />
      <View style={{ marginVertical: 10 }} />
      <Button
        title="Mind Content Library"
        onPress={() => navigation.navigate("MindContentLibrary")}
      />
    </View>
  );
};


function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="MainHome">
        <Stack.Screen
          name="MainHome"
          component={MainHomeScreen}
          options={{ title: "RealValue Home" }}
        />
        <Stack.Screen
          name="HealthCheck"
          component={HealthCheckScreen}
          options={{ title: "Backend Health" }}
        />
        <Stack.Screen
          name="PracticeChallenges"
          component={PracticeChallengesScreen}
          options={{ title: "Practice Challenges" }}
        />
        <Stack.Screen
          name="ChallengeAttempt"
          component={ChallengeAttemptScreen}
          options={({ route }) => ({
            title: "Attempt Challenge",
            // Potentially set title based on route.params.challenge?.title if fetched early
          })}
        />
        <Stack.Screen
          name="MyCompletions"
          component={MyCompletionsScreen}
          options={{ title: "My Completions" }}
        />
        <Stack.Screen
          name="MindContentLibrary"
          component={MindContentLibraryScreen}
          options={{ title: "Mind Content Library" }}
        />
        <Stack.Screen
          name="MindContentForm"
          component={MindContentFormScreen}
          options={({ route }) => ({
            title: route.params?.mode === 'edit' ? "Edit Content" : "Suggest Content"
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default App;
