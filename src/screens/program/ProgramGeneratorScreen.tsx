import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { AssessmentForm } from '../../components/program/AssessmentForm';
import { ProgramDisplay } from '../../components/program/ProgramDisplay';
import programGeneratorService, { 
  StreetliftingAssessment, 
  GeneratedProgram 
} from '../../services/api/programGenerator';

type ScreenState = 'assessment' | 'program' | 'loading';

export const ProgramGeneratorScreen: React.FC = () => {
  const [screenState, setScreenState] = useState<ScreenState>('assessment');
  const [generatedProgram, setGeneratedProgram] = useState<GeneratedProgram | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAssessmentSubmit = async (assessment: StreetliftingAssessment) => {
    console.log('🔥 BUTTON CLICKED! Starting program generation...');
    console.log('Assessment data:', assessment);
    
    setLoading(true);
    setScreenState('loading');

    try {
      console.log('📡 Calling LLM API...');
      // Use real LLM API to generate the program
      const generatedProgram = await programGeneratorService.generateProgram(assessment);
      console.log('✅ LLM API responded:', generatedProgram);
      setGeneratedProgram(generatedProgram);
      setScreenState('program');
      
    } catch (error) {
      console.error('❌ Program generation failed:', error);
      
      // Fallback to mock generation if API fails
      console.warn('🔄 API failed, using fallback simulation...');
      try {
        const mockProgram = await simulateProgramGeneration(assessment);
        console.log('✅ Fallback completed:', mockProgram);
        setGeneratedProgram(mockProgram);
        setScreenState('program');
        
        Alert.alert(
          'Offline Mode',
          'Using offline program generation. For AI-powered programs, make sure the Python server is running.',
          [{ text: 'OK' }]
        );
      } catch (fallbackError) {
        Alert.alert(
          'Generation Failed',
          'Unable to generate your program. Please try again.',
          [{ text: 'OK', onPress: () => setScreenState('assessment') }]
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const simulateProgramGeneration = async (
    assessment: StreetliftingAssessment
  ): Promise<GeneratedProgram> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate a mock program based on your actual program generator logic
    const weekly_program: Record<number, string> = {};
    
    for (let day = 1; day <= assessment.training_days_per_week; day++) {
      weekly_program[day] = generateMockSession(assessment, day);
    }
    
    return {
      id: Date.now().toString(),
      weekly_program,
      assessment,
      created_at: new Date().toISOString(),
    };
  };

  const generateMockSession = (assessment: StreetliftingAssessment, day: number): string => {
    const meso = `MESO${Math.floor((assessment.mesocycle_week - 1) / 4) + 1}`;
    
    if (day % 2 === 1) { // Streetlifting days
      if (day === 1) {
        const weight = Math.max(5, Math.floor(assessment.weighted_pullups_max * 0.8));
        return `${meso} — GIORNO ${day} — Prescription: Trazioni Wide Grip - reset tra le ripetizioni e singole spezzate (Filma solo ultimo set) - ${weight}kg
Lavoriamo cercando di migliorare oscillazione in partenza (ricerchiamo il pendolo) e scapole attive in partenza | Week data: 5 x 1+1, rest 15"/20" miniset, 1:30 - 2:00 tra i set.
Filma ultimo set`;
      } else {
        const weight = Math.max(5, Math.floor(assessment.weighted_dips_max * 0.8));
        return `${meso} — GIORNO ${day} — Prescription: Dips Parallele - controllo fase negativa (Filma ultimo set) - ${weight}kg
Focus su scapole depresse e addotte durante tutto il movimento e gomiti vicino al corpo, non aperti lateralmente | Week data: 6 x 2, rest 2:00 - 2:30 tra i set.
Filma ultimo set`;
      }
    } else { // Compound days
      if (day === 2) {
        const weight = Math.max(20, Math.floor(assessment.rows_max * 0.8));
        return `${meso} — GIORNO ${day} — Prescription: Bent Over Row - focus ipertrofia dorsali (Filma serie centrali) - ${weight}kg
Lavoriamo su scapole retratte e depresse e squeeze delle scapole in contrazione | Week data: 4 x 6-8, rest 2:00 - 2:30 tra i set.
Filma serie 2 e 3`;
      } else {
        const weight = Math.max(40, Math.floor(assessment.squats_max * 0.8));
        return `${meso} — GIORNO ${day} — Prescription: Back Squat - sviluppo forza gambe (Filma ultimo set) - ${weight}kg
Focus tecnico su discesa controllata sotto il parallelo e core stabile durante tutto il movimento | Week data: 4 x 8-10, rest 2:30 - 3:00 tra i set.
Filma ultimo set`;
      }
    }
  };

  const handleDayPress = (day: number, session: string) => {
    Alert.alert(
      `Day ${day} - Full Session`,
      session,
      [{ text: 'Start Workout', onPress: () => console.log('Start workout for day', day) }]
    );
  };

  const handleNewProgram = () => {
    setScreenState('assessment');
    setGeneratedProgram(null);
  };

  if (screenState === 'loading') {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingTitle}>🤖 LLM Generating Your Program</Text>
        <Text style={styles.loadingText}>
          Using fine-tuned AI model to analyze your fitness level and create personalized streetlifting workouts...
        </Text>
        <View style={styles.loadingDots}>
          <Text style={styles.loadingDotsText}>●●●</Text>
        </View>
      </View>
    );
  }

  if (screenState === 'program' && generatedProgram) {
    return (
      <View style={styles.container}>
        <TouchableOpacity 
          style={styles.newProgramButton}
          onPress={handleNewProgram}
        >
          <Text style={styles.newProgramButtonText}>Generate New Program</Text>
        </TouchableOpacity>
        <ProgramDisplay 
          program={generatedProgram} 
          onDayPress={handleDayPress}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <AssessmentForm 
        onSubmit={handleAssessmentSubmit}
        loading={loading}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 20,
  },
  loadingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 15,
    textAlign: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  loadingDots: {
    padding: 20,
  },
  loadingDotsText: {
    fontSize: 24,
    color: '#2563eb',
    textAlign: 'center',
  },
  newProgramButton: {
    backgroundColor: '#059669',
    margin: 20,
    padding: 15,
    borderRadius: 8,
    marginBottom: 0,
  },
  newProgramButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
});