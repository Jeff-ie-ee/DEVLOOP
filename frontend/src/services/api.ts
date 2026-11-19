const API_BASE_URL = 'http://127.0.0.1:8000'

export interface ApiHealth {
  status: string
  service: string
}

export interface DatabaseHealth {
  status: string
  database: string
}

export async function getApiHealth(): Promise<ApiHealth> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error('API health check failed')
  }

  return response.json() as Promise<ApiHealth>
}

export async function getDatabaseHealth(): Promise<DatabaseHealth> {
  const response = await fetch(`${API_BASE_URL}/health/database`)

  if (!response.ok) {
    throw new Error('Database health check failed')
  }

  return response.json() as Promise<DatabaseHealth>
}
