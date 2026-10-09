import styles from './Stepper.module.css';

/**
 * Multi-step flow progress. Completed steps can be clicked to go back; later steps unlock in
 * order. The current step is marked with ink and weight, not color.
 */
export default function Stepper({ steps, current, onStepClick }) {
  return (
    <ol className={styles.stepper}>
      {steps.map((label, index) => {
        const state = index < current ? 'done' : index === current ? 'current' : 'todo';
        const text = `${index + 1} ${label}`;

        return (
          <li key={label} className={`${styles.step} ${styles[state]}`}>
            <span className={styles.bar} aria-hidden="true" />
            {state === 'done' && onStepClick ? (
              <button type="button" className={styles.link} onClick={() => onStepClick(index)}>
                <span aria-hidden="true">✓ </span>
                {text}
                <span className={styles.srOnly}> (completed)</span>
              </button>
            ) : (
              <span aria-current={state === 'current' ? 'step' : undefined}>
                {state === 'done' ? <span aria-hidden="true">✓ </span> : null}
                {text}
                {state === 'done' ? <span className={styles.srOnly}> (completed)</span> : null}
              </span>
            )}
          </li>
        );
      })}
    </ol>
  );
}
