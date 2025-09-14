import apiClient from './client';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  user?: {
    id: number;
    username: string;
    email: string;
  };
  message?: string;
  error?: string;
}

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        '/api/auth/login',
        credentials
      );
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async signup(userData: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        '/api/auth/signup',
        userData
      );
      return response;
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/auth/logout', {});
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }
}

export default new AuthService();