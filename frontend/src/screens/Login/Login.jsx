import { useEffect, useState } from 'react';

import { Banner, Button, Card, Field } from '../../components/index.js';
import { ApiError, DEMO_TENANTS, api, getTenant, setTenant } from '../../lib/api.js';
import styles from './Login.module.css';

/**
 * Demo login: pick a tenant, enter username/password, then the MFA code when
 * the account has a TOTP device. Calls onLoggedIn(username) on success.
 */
export default function Login({ onLoggedIn }) {
  const [tenant, setTenantChoice] = useState(getTenant());
  const [username, setUsername] = useState('demo');
  const [password, setPassword] = useState('');
  const [mfaStep, setMfaStep] = useState(false);
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  // The login POST needs the CSRF token fetched below; the button stays
  // disabled until it arrives so a fast click can't 403 (increment 1.10.3).
  const [csrfReady, setCsrfReady] = useState(false);

  useEffect(() => {
    api.csrf().then(
      () => setCsrfReady(true),
      () => {
        setError('Could not reach the server. Check your connection.');
      },
    );
  }, []);

  function fail(err) {
    setError(err instanceof ApiError ? err.message : 'Something went wrong.');
    setBusy(false);
  }

  async function submitCredentials(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    setTenant(tenant);
    try {
      const { mfa_required } = await api.login(username, password);
      if (mfa_required) {
        setMfaStep(true);
      } else {
        onLoggedIn(username);
      }
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function submitMfa(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await api.mfa(token);
      onLoggedIn(username);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.page}>
      <Card>
        <h2 className={styles.title}>Log in to Cascadia</h2>
        <p className={styles.demo}>
          Demo environment — sign in with username <strong>demo</strong> and password{' '}
          <strong>demo-pass</strong>.
        </p>
        {error ? (
          <Banner variant="error" title="Could not log in">
            {error}
          </Banner>
        ) : null}
        {!mfaStep ? (
          <form onSubmit={submitCredentials} className={styles.form}>
            <label className={styles.label} htmlFor="tenant">
              Lending organization
            </label>
            <select
              id="tenant"
              className={styles.select}
              value={tenant}
              onChange={(e) => setTenantChoice(e.target.value)}
            >
              {DEMO_TENANTS.map((t) => (
                <option key={t.schema} value={t.schema}>
                  {t.label}
                </option>
              ))}
            </select>
            <Field
              label="Username"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <Field
              label="Password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" variant="primary" busy={busy} disabled={!csrfReady}>
              Log in
            </Button>
          </form>
        ) : (
          <form onSubmit={submitMfa} className={styles.form}>
            <p className={styles.mfaHint}>
              This account uses two-step verification. Enter the 6-digit code from your
              authenticator app.
            </p>
            <Field
              label="Authenticator code"
              name="token"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
            <Button type="submit" variant="primary" busy={busy}>
              Verify
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}
