import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { StreetliftingAssessment } from '../../services/api/programGenerator';

interface AssessmentFormProps {
  onSubmit: (assessment: StreetliftingAssessment) => void;
  loading?: boolean;
}

export const AssessmentForm: React.FC<AssessmentFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const [assessment, setAssessment] = useState<StreetliftingAssessment>({
    weighted_pullups_max: 0,
    weighted_dips_max: 0,
    muscle_ups: 0,
    rows_max: 0,
    pushups_max: 0,
    squats_max: 0,
    training_days_per_week: 3,
    mesocycle_week: 1,
    primary_goal: 'strength',
  });

  const goals = [
    { key: 'strength', label: 'Strength Development' },
    { key: 'muscle_ups', label: 'Muscle-Up Progression' },
    { key: 'hypertrophy', label: 'Muscle Building' },
    { key: 'power', label: 'Power & Explosiveness' },
  ];

  const handleSubmit = () => {
    Alert.alert('DEBUG', 'Button clicked! Form is working.');
    
    if (assessment.training_days_per_week < 1 || assessment.training_days_per_week > 7) {
      Alert.alert('Error', 'Training days must be between 1 and 7');
      return;
    }
    
    onSubmit(assessment);
  };

  const updateField = (field: keyof StreetliftingAssessment, value: string | number) => {
    setAssessment(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Fitness Assessment</Text>
      <Text style={styles.subtitle}>
        Help us create your personalized streetlifting program
      </Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💪 Core Streetlifting Movements</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Weighted Pull-ups Max (kg)</Text>
          <TextInput
            style={styles.input}
            value={assessment.weighted_pullups_max.toString()}
            onChangeText={(text) => updateField('weighted_pullups_max', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="25"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Weighted Dips Max (kg)</Text>
          <TextInput
            style={styles.input}
            value={assessment.weighted_dips_max.toString()}
            onChangeText={(text) => updateField('weighted_dips_max', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="30"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Muscle-ups Max (reps)</Text>
          <TextInput
            style={styles.input}
            value={assessment.muscle_ups.toString()}
            onChangeText={(text) => updateField('muscle_ups', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="4"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏋️ Compound Movements</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Weighted Rows Max (kg)</Text>
          <TextInput
            style={styles.input}
            value={assessment.rows_max.toString()}
            onChangeText={(text) => updateField('rows_max', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="60"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Push-ups Max (reps)</Text>
          <TextInput
            style={styles.input}
            value={assessment.pushups_max.toString()}
            onChangeText={(text) => updateField('pushups_max', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="35"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Squats Max (kg)</Text>
          <TextInput
            style={styles.input}
            value={assessment.squats_max.toString()}
            onChangeText={(text) => updateField('squats_max', parseInt(text) || 0)}
            keyboardType="numeric"
            placeholder="80"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📅 Training Schedule</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Training Days per Week</Text>
          <TextInput
            style={styles.input}
            value={assessment.training_days_per_week.toString()}
            onChangeText={(text) => updateField('training_days_per_week', parseInt(text) || 3)}
            keyboardType="numeric"
            placeholder="3"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Current Mesocycle Week</Text>
          <TextInput
            style={styles.input}
            value={assessment.mesocycle_week.toString()}
            onChangeText={(text) => updateField('mesocycle_week', parseInt(text) || 1)}
            keyboardType="numeric"
            placeholder="1"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Primary Goal</Text>
        {goals.map((goal) => (
          <TouchableOpacity
            key={goal.key}
            style={[
              styles.goalButton,
              assessment.primary_goal === goal.key && styles.goalButtonSelected
            ]}
            onPress={() => updateField('primary_goal', goal.key)}
          >
            <Text style={[
              styles.goalButtonText,
              assessment.primary_goal === goal.key && styles.goalButtonTextSelected
            ]}>
              {goal.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={loading}
      >
        <Text style={styles.submitButtonText}>
          {loading ? 'Generating Program...' : 'Generate My Program'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8f9fa',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2563eb',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 30,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 15,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  goalButton: {
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  goalButtonSelected: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  goalButtonText: {
    fontSize: 16,
    color: '#374151',
    textAlign: 'center',
  },
  goalButtonTextSelected: {
    color: '#2563eb',
    fontWeight: '600',
  },
  submitButton: {
    backgroundColor: '#2563eb',
    padding: 16,
    borderRadius: 8,
    marginTop: 20,
    marginBottom: 40,
  },
  submitButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
});