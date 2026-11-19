
import { useEffect, useState } from 'react'
import {
  getApiHealth,
  getDatabaseHealth,
  type ApiHealth,
  type DatabaseHealth,
} from './services/api'

// Fetch API and database health information.
async function fetchConnections(): Promise<
  [ApiHealth, DatabaseHealth]
> {
  return Promise.all([
    getApiHealth(),
    getDatabaseHealth(),
  ])
}

function App() {
  const [apiHealth, setApiHealth] = useState<ApiHealth | null>(null)
  const [databaseHealth, setDatabaseHealth] =
    useState<DatabaseHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastChecked, setLastChecked] = useState<string | null>(null)

  // Manual connection refresh.
  async function checkConnections() {
    setLoading(true)

    try {
      const [apiResult, databaseResult] = await fetchConnections()

      setApiHealth(apiResult)
      setDatabaseHealth(databaseResult)
      setLastChecked(new Date().toLocaleTimeString())
    } catch {
      setApiHealth(null)
      setDatabaseHealth(null)
      setLastChecked(new Date().toLocaleTimeString())
    } finally {
      setLoading(false)
    }
  }

  // Initial connection check when the dashboard loads.
  useEffect(() => {
    let active = true

    fetchConnections()
      .then(([apiResult, databaseResult]) => {
        if (!active) return

        setApiHealth(apiResult)
        setDatabaseHealth(databaseResult)
        setLastChecked(new Date().toLocaleTimeString())
      })
      .catch(() => {
        if (!active) return

        setApiHealth(null)
        setDatabaseHealth(null)
        setLastChecked(new Date().toLocaleTimeString())
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [])

  const apiConnected = apiHealth?.status === 'healthy'
  const databaseConnected = databaseHealth?.status === 'connected'

  const modules = [
    {
      number: '01',
      name: 'Problem Management',
      description: 'Organise coding problems and assessments.',
    },
    {
      number: '02',
      name: 'Secure Execution',
      description: 'Run code in an isolated execution environment.',
    },
    {
      number: '03',
      name: 'Adaptive Evaluation',
      description: 'Evaluate solutions using configurable test cases.',
    },
    {
      number: '04',
      name: 'Code Intelligence',
      description: 'Analyse code quality and engineering metrics.',
    },
    {
      number: '05',
      name: 'Reproducibility',
      description: 'Track execution records and evidence.',
    },
    {
      number: '06',
      name: 'Developer Analytics',
      description: 'Understand progress through measurable insights.',
    },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-900/80 p-6 md:flex md:flex-col">
          <div>
            <h1 className="text-2xl font-bold tracking-wider text-white">
              DEVLOOP
            </h1>

            <p className="mt-1 text-xs tracking-widest text-slate-500">
              LEARN. RESEARCH. BUILD. EVOLVE.
            </p>
          </div>

          <nav className="mt-12 space-y-2">
            <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">
              Workspace
            </p>

            {[
              'Overview',
              'My Projects',
              'Problem Library',
              'Code Workspace',
              'Code Intelligence',
              'Analytics',
              'Settings',
            ].map((item, index) => (
              <div
                key={item}
                className={`rounded-lg px-4 py-3 text-sm ${
                  index === 0
                    ? 'bg-indigo-500/15 font-semibold text-indigo-300'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {item}
              </div>
            ))}
          </nav>

          <div className="mt-auto rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs font-semibold text-slate-400">
              DEVELOPER WORKSPACE
            </p>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              A unified environment for software engineering productivity
              and code intelligence.
            </p>
          </div>
        </aside>

        {/* Main workspace */}
        <main className="min-w-0 flex-1 p-5 sm:p-8 lg:p-10">

          {/* Header */}
          <header className="mb-10 flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">
                Personal Workspace
              </p>

              <h2 className="mt-1 text-2xl font-semibold text-white sm:text-3xl">
                Overview
              </h2>
            </div>

            <div className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2">
              <span className="h-2 w-2 rounded-full bg-indigo-400" />

              <span className="text-sm text-slate-300">
                Developer Workspace
              </span>
            </div>
          </header>

          {/* Hero section */}
          <section className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-900 p-7 sm:p-10">
            <div className="relative z-10 max-w-2xl">
              <p className="text-xs font-semibold tracking-[0.25em] text-indigo-300">
                DEVELOPER ENGINEERING & INTELLIGENCE PLATFORM
              </p>

              <h1 className="mt-5 text-3xl font-bold leading-tight text-white sm:text-5xl">
                Build better software through measurable engineering.
              </h1>

              <p className="mt-5 max-w-xl text-sm leading-7 text-slate-300 sm:text-base">
                A unified workspace for secure code execution, adaptive
                evaluation, code intelligence and reproducible software
                quality.
              </p>

              <button
                onClick={() =>
                  document
                    .getElementById('workspace-modules')
                    ?.scrollIntoView({ behavior: 'smooth' })
                }
                className="mt-7 rounded-lg bg-indigo-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400"
              >
                Explore Workspace
              </button>
            </div>

            <div className="pointer-events-none absolute -right-20 -top-24 h-80 w-80 rounded-full border border-indigo-400/10" />

            <div className="pointer-events-none absolute -right-8 -top-12 h-56 w-56 rounded-full border border-indigo-400/10" />
          </section>

          {/* Statistics */}
          <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              { label: 'Active Projects', value: '00' },
              { label: 'Problems Solved', value: '00' },
              { label: 'Code Executions', value: '00' },
              { label: 'Quality Reports', value: '00' },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-slate-800 bg-slate-900 p-5"
              >
                <p className="text-sm text-slate-400">
                  {stat.label}
                </p>

                <p className="mt-4 text-3xl font-semibold text-white">
                  {stat.value}
                </p>

                <p className="mt-2 text-xs text-slate-600">
                  Workspace activity will appear here
                </p>
              </div>
            ))}
          </section>

          {/* Workspace modules */}
          <section id="workspace-modules" className="mt-12">
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-widest text-indigo-400">
                Platform capabilities
              </p>

              <h2 className="mt-2 text-xl font-semibold text-white">
                Workspace Modules
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Core engineering capabilities of the DEVLOOP platform.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {modules.map((module) => (
                <div
                  key={module.number}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-indigo-500/40"
                >
                  <p className="text-sm font-semibold text-indigo-400">
                    {module.number}
                  </p>

                  <h3 className="mt-4 font-semibold text-white">
                    {module.name}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {module.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Infrastructure monitoring */}
          <section className="mt-12 rounded-xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-indigo-400">
                  Infrastructure
                </p>

                <h2 className="mt-2 text-xl font-semibold text-white">
                  System Connection Status
                </h2>

                <p className="mt-2 text-sm text-slate-400">
                  Live connection checks from the DEVLOOP backend.
                </p>
              </div>

              <button
                onClick={() => void checkConnections()}
                disabled={loading}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 transition hover:bg-slate-800 disabled:opacity-50"
              >
                {loading ? 'Checking...' : 'Refresh Status'}
              </button>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">

              {/* Backend status */}
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-5">
                <p className="text-sm text-slate-400">
                  FastAPI Backend
                </p>

                <div className="mt-3 flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      loading
                        ? 'bg-amber-400'
                        : apiConnected
                          ? 'bg-emerald-400'
                          : 'bg-red-400'
                    }`}
                  />

                  <span className="font-semibold text-white">
                    {loading
                      ? 'Checking connection'
                      : apiConnected
                        ? 'Connected'
                        : 'Disconnected'}
                  </span>
                </div>

                <p className="mt-2 text-xs text-slate-500">
                  {apiHealth?.service ?? 'DEVLOOP API'}
                </p>
              </div>

              {/* Database status */}
              <div className="rounded-lg border border-slate-800 bg-slate-950 p-5">
                <p className="text-sm text-slate-400">
                  PostgreSQL Database
                </p>

                <div className="mt-3 flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      loading
                        ? 'bg-amber-400'
                        : databaseConnected
                          ? 'bg-emerald-400'
                          : 'bg-red-400'
                    }`}
                  />

                  <span className="font-semibold text-white">
                    {loading
                      ? 'Checking connection'
                      : databaseConnected
                        ? 'Connected'
                        : 'Disconnected'}
                  </span>
                </div>

                <p className="mt-2 text-xs text-slate-500">
                  {databaseHealth?.database ?? 'PostgreSQL'}
                </p>
              </div>
            </div>

            <p className="mt-5 text-xs text-slate-500">
              Last checked: {lastChecked ?? 'Not checked yet'}
            </p>
          </section>

          {/* Development activity */}
          <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="font-semibold text-white">
              Development Activity
            </h2>

            <p className="mt-3 text-sm text-slate-500">
              Your engineering activity and execution history will appear
              here as platform modules are developed.
            </p>
          </section>

          {/* Footer */}
          <footer className="mt-12 border-t border-slate-800 pt-6 text-center text-xs text-slate-600">
            DEVLOOP · Developer Engineering & Intelligence Platform
          </footer>
        </main>
      </div>
    </div>
  )
}

export default App
