import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { GeneratedProgram } from '../../services/api/programGenerator';

interface ProgramDisplayProps {
  program: GeneratedProgram;
  onDayPress?: (day: number, session: string) => void;
}

export const ProgramDisplay: React.FC<ProgramDisplayProps> = ({
  program,
  onDayPress,
}) => {
  const parsePrescription = (session: string) => {
    const lines = session.split('\n');
    const prescription = lines.find(line => line.startsWith('Prescription:'));
    const weekData = lines.find(line => line.includes('Week data:'));
    const filming = lines.find(line => line.includes('Filma'));
    
    return {
      prescription: prescription?.replace('Prescription:', '').trim() || '',
      weekData: weekData || '',
      filming: filming || '',
    };
  };

  const getDayEmoji = (day: number) => {
    const emojis = ['💪', '🔥', '⚡', '🚀', '💯', '🎯', '✨'];
    return emojis[(day - 1) % emojis.length];
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Your Training Program</Text>
      
      <View style={styles.programInfo}>
        <Text style={styles.programInfoText}>
          Goal: {program.assessment.primary_goal.toUpperCase()}
        </Text>
        <Text style={styles.programInfoText}>
          {program.assessment.training_days_per_week} days/week • Week {program.assessment.mesocycle_week}
        </Text>
      </View>

      {Object.entries(program.weekly_program).map(([dayStr, session]) => {
        const day = parseInt(dayStr);
        const parsed = parsePrescription(session);
        
        return (
          <TouchableOpacity
            key={day}
            style={styles.dayCard}
            onPress={() => onDayPress?.(day, session)}
          >
            <View style={styles.dayHeader}>
              <Text style={styles.dayNumber}>
                {getDayEmoji(day)} Day {day}
              </Text>
            </View>
            
            <Text style={styles.exerciseTitle}>
              {parsed.prescription}
            </Text>
            
            {parsed.weekData && (
              <Text style={styles.weekData}>
                {parsed.weekData}
              </Text>
            )}
            
            {parsed.filming && (
              <View style={styles.filmingNote}>
                <Text style={styles.filmingText}>📹 {parsed.filming}</Text>
              </View>
            )}
            
            <View style={styles.tapHint}>
              <Text style={styles.tapHintText}>Tap for full session details</Text>
            </View>
          </TouchableOpacity>
        );
      })}
      
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          💡 Follow the technical cues and rest periods for optimal results
        </Text>
      </View>
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
    marginBottom: 20,
  },
  programInfo: {
    backgroundColor: '#eff6ff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#2563eb',
  },
  programInfoText: {
    fontSize: 16,
    color: '#1e40af',
    fontWeight: '500',
    textAlign: 'center',
  },
  dayCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  dayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  dayNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  exerciseTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2563eb',
    marginBottom: 10,
    lineHeight: 22,
  },
  weekData: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 10,
    fontStyle: 'italic',
  },
  filmingNote: {
    backgroundColor: '#fef3c7',
    padding: 8,
    borderRadius: 6,
    marginBottom: 10,
  },
  filmingText: {
    fontSize: 14,
    color: '#92400e',
    fontWeight: '500',
  },
  tapHint: {
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 10,
  },
  tapHintText: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  footer: {
    backgroundColor: '#f3f4f6',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
    marginBottom: 40,
  },
  footerText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});