
import { useState } from 'react'
import './App.css'
import Onboarding, {
  type FreelancerProfile,
} from './components/Onboarding'

function App() {
  const [profile, setProfile] = useState<FreelancerProfile | null>(null)

  if (profile) {
    return (
      <main style={{ padding: '48px 24px', textAlign: 'center' }}>
        <h1>You're ready, {profile.displayName}!</h1>
        <p>
          Your work type is {profile.workType}. Your financial health
          check will use South African rand (R).
        </p>
        <p>
          Your profile is ready. The next step is to connect the
          financial health form when it is available.
        </p>
        <button onClick={() => setProfile(null)}>
          Back to profile
        </button>
      </main>
    )
  }

  return <Onboarding onContinue={setProfile} />
}

export default App
