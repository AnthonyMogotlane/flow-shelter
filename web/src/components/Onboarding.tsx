
import { useState, type FormEvent } from 'react'
import './Onboarding.css'

export interface FreelancerProfile {
  displayName: string
  workType: string
}

interface OnboardingProps {
  onContinue: (profile: FreelancerProfile) => void
}

const workTypes = [
  'Designer',
  'Developer',
  'Writer or content creator',
  'Consultant',
  'Tradesperson',
  'Virtual assistant',
  'Other',
]

export default function Onboarding({ onContinue }: OnboardingProps) {
  const [displayName, setDisplayName] = useState('')
  const [workType, setWorkType] = useState('')
  const [error, setError] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!displayName.trim() || !workType) {
      setError('Please enter your name and select your type of work.')
      return
    }

    setError('')
    onContinue({
      displayName: displayName.trim(),
      workType,
    })
  }

  return (
    <main className="onboarding">
      <header className="onboarding-header">
        <span className="onboarding-brand">FlowShelter</span>
        <span className="onboarding-currency">
          Built for South Africa · ZAR (R)
        </span>
      </header>

      <section className="onboarding-content">
        <div className="onboarding-intro">
          <span className="onboarding-eyebrow">
            YOUR FINANCIAL WELLNESS JOURNEY
          </span>
          <h1>Make your money work between paydays.</h1>
          <p>
            Freelance income can change from month to month.
            FlowShelter helps you understand your financial health
            and plan with more confidence.
          </p>
        </div>

        <form className="onboarding-form" onSubmit={handleSubmit}>
          <h2>Let&apos;s get to know you</h2>
          <p className="onboarding-helper">
            Just two quick details. No account or banking information needed.
          </p>

          <div className="onboarding-field">
            <label htmlFor="displayName">What should we call you?</label>
            <input
              id="displayName"
              name="displayName"
              type="text"
              autoComplete="nickname"
              placeholder="Enter your display name"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              required
              maxLength={60}
            />
          </div>

          <div className="onboarding-field">
            <label htmlFor="workType">
              What kind of freelance work do you do?
            </label>
            <select
              id="workType"
              name="workType"
              value={workType}
              onChange={(event) => setWorkType(event.target.value)}
              required
            >
              <option value="">Choose your work type</option>
              {workTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <p className="onboarding-rand-note">
            Your financial health check will use South African rand (R).
            You won&apos;t need to share your bank details or ID number.
          </p>

          {error && (
            <p className="onboarding-error" role="alert">
              {error}
            </p>
          )}

          <button className="onboarding-submit" type="submit">
            Start my financial health check
            <span aria-hidden="true"> →</span>
          </button>

          <p className="onboarding-privacy">
            A simple prototype to help you take control of your finances.
          </p>
        </form>
      </section>
    </main>
  )
}
