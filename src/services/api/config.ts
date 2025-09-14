const API_CONFIG = {
  BASE_URL: 'http://213.181.111.2:3002',
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      REFRESH: '/auth/refresh',
      LOGOUT: '/auth/logout',
    },
    USERS: {
      PROFILE: '/users/profile',
      UPDATE_PROFILE: '/users/profile',
    },
    PROGRAMS: {
      GENERATE: '/programs/generate',
      GET_USER_PROGRAMS: '/programs/user',
      UPDATE_PROGRAM: '/programs',
    },
    WORKOUTS: {
      START_SESSION: '/workouts/session/start',
      END_SESSION: '/workouts/session/end',
      UPDATE_SESSION: '/workouts/session',
    },
    FEEDBACK: {
      SUBMIT: '/feedback',
      GET_USER_FEEDBACK: '/feedback/user',
    },
  },
  TIMEOUT: 10000,
};

export default API_CONFIG;