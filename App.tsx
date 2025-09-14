import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { ProgramGeneratorScreen } from './src/screens/program/ProgramGeneratorScreen';
import { LoginScreen } from './src/screens/auth/LoginScreen';
import { SignupScreen } from './src/screens/auth/SignupScreen';

type AppState = 'login' | 'signup' | 'app';

export default function App() {
  const [appState, setAppState] = useState<AppState>('login');
  const [user, setUser] = useState<any>(null);

  const handleLoginSuccess = (userData: any) => {
    setUser(userData);
    setAppState('app');
  };

  const handleSignupSuccess = () => {
    setAppState('login');
  };

  const renderScreen = () => {
    switch (appState) {
      case 'login':
        return (
          <LoginScreen
            onLoginSuccess={handleLoginSuccess}
            onSwitchToSignup={() => setAppState('signup')}
          />
        );
      case 'signup':
        return (
          <SignupScreen
            onSignupSuccess={handleSignupSuccess}
            onSwitchToLogin={() => setAppState('login')}
          />
        );
      case 'app':
        return <ProgramGeneratorScreen />;
      default:
        return (
          <LoginScreen
            onLoginSuccess={handleLoginSuccess}
            onSwitchToSignup={() => setAppState('signup')}
          />
        );
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      {renderScreen()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
});
