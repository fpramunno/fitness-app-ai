import apiClient from './client';
import { ProgramGenerationRequest, Program } from '../../types';

export interface StreetliftingAssessment {
  weighted_pullups_max: number;
  weighted_dips_max: number;
  muscle_ups: number;
  rows_max: number;
  pushups_max: number;
  squats_max: number;
  training_days_per_week: number;
  mesocycle_week: number;
  primary_goal: 'strength' | 'muscle_ups' | 'hypertrophy' | 'power';
}

export interface GeneratedProgram {
  id: string;
  weekly_program: Record<number, string>;
  assessment: StreetliftingAssessment;
  created_at: string;
}

class ProgramGeneratorService {
  async generateProgram(assessment: StreetliftingAssessment): Promise<GeneratedProgram> {
    try {
      const response = await apiClient.post<GeneratedProgram>(
        '/api/generate-program',
        assessment
      );
      return response;
    } catch (error) {
      console.error('Program generation failed:', error);
      throw error;
    }
  }

  async getUserPrograms(userId: string): Promise<GeneratedProgram[]> {
    try {
      const response = await apiClient.get<GeneratedProgram[]>(
        `/api/programs/user/${userId}`
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch user programs:', error);
      throw error;
    }
  }

  async updateProgramFeedback(
    programId: string, 
    feedback: {
      day: number;
      rating: number;
      difficulty: number;
      notes?: string;
    }
  ): Promise<void> {
    try {
      await apiClient.post(`/api/programs/${programId}/feedback`, feedback);
    } catch (error) {
      console.error('Failed to submit program feedback:', error);
      throw error;
    }
  }
}

export default new ProgramGeneratorService();