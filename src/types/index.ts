export interface User {
  id: string;
  email: string;
  name: string;
  age?: number;
  weight?: number;
  height?: number;
  fitnessLevel: 'beginner' | 'intermediate' | 'advanced';
  goals: string[];
  equipment: string[];
  availableTime: number; // minutes per workout
  workoutDaysPerWeek: number;
}

export interface Exercise {
  id: string;
  name: string;
  description: string;
  muscleGroups: string[];
  equipment: string[];
  instructions: string[];
  videoUrl?: string;
  imageUrl?: string;
}

export interface WorkoutSet {
  exerciseId: string;
  sets: number;
  reps: number | string; // can be "8-12" for ranges
  weight?: number;
  restTime: number; // seconds
  notes?: string;
}

export interface Workout {
  id: string;
  name: string;
  description: string;
  exercises: WorkoutSet[];
  estimatedDuration: number; // minutes
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
}

export interface Program {
  id: string;
  name: string;
  description: string;
  duration: number; // weeks
  workouts: Workout[];
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkoutSession {
  id: string;
  workoutId: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  completed: boolean;
  exercises: CompletedExercise[];
  notes?: string;
  rating?: number; // 1-5
  difficulty?: number; // 1-5
}

export interface CompletedExercise {
  exerciseId: string;
  sets: CompletedSet[];
  notes?: string;
}

export interface CompletedSet {
  reps: number;
  weight?: number;
  restTime?: number;
  completed: boolean;
}

export interface Feedback {
  id: string;
  userId: string;
  workoutSessionId: string;
  rating: number; // 1-5
  difficulty: number; // 1-5
  enjoyment: number; // 1-5
  fatigue: number; // 1-5
  comments?: string;
  suggestions?: string;
  createdAt: Date;
}

export interface ProgramGenerationRequest {
  userId: string;
  goals: string[];
  fitnessLevel: 'beginner' | 'intermediate' | 'advanced';
  equipment: string[];
  availableTime: number;
  workoutDaysPerWeek: number;
  duration: number; // weeks
  preferences?: string[];
}