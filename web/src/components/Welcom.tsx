import './Welcom.css'

interface WelcomeProps {
  teamName: string;
  appName: string;
  slogan: string;
}

export default function Welcome({ teamName, appName, slogan }: WelcomeProps) {
  return (
    <div className="welcome">
      <svg
        className="welcome-mark"
        viewBox="0 0 137 117"
        role="img"
        aria-label={`${appName} logo`}
      >
        <path d="M15 7h107v107H57c4-7 4-15 0-22h46V27H35v45H15z" />
        <circle cx="25.5" cy="102.5" r="15.5" />
      </svg>
      <div></div>
      <div></div>
      <h1>Welcome, <span>{teamName}</span>!</h1>
      <div></div>
      <div></div>
      <p>This is <strong>{appName}</strong>, we say "{slogan}"</p>
    </div>
  );
}