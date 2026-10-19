import { useState } from 'react';

import { Button } from './components/index.js';
import { api } from './lib/api.js';
import FundDetail from './screens/Funds/FundDetail.jsx';
import FundsList from './screens/Funds/FundsList.jsx';
import Login from './screens/Login/Login.jsx';
import styles from './App.module.css';

/**
 * Demo UI shell (increment 1.10): login with MFA, then the funds dashboard.
 * State-based navigation is fine for the demo slice; a router arrives later.
 */
export default function App() {
  const [username, setUsername] = useState(null);
  const [fundId, setFundId] = useState(null);

  async function logout() {
    try {
      await api.logout();
    } finally {
      setUsername(null);
      setFundId(null);
    }
  }

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1 className={styles.brand}>Cascadia</h1>
        {username ? (
          <div className={styles.user}>
            <span className={styles.username}>{username}</span>
            <Button variant="ghost" onClick={logout}>
              Log out
            </Button>
          </div>
        ) : null}
      </header>
      <main>
        {!username ? (
          <Login onLoggedIn={setUsername} />
        ) : fundId === null ? (
          <FundsList onSelect={setFundId} />
        ) : (
          <FundDetail fundId={fundId} onBack={() => setFundId(null)} />
        )}
      </main>
    </div>
  );
}
