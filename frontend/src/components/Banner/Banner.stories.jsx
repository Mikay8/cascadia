import Button from '../Button/Button.jsx';
import Banner from './Banner.jsx';

export default {
  title: 'Components/Banner',
  component: Banner,
  parameters: { layout: 'fullscreen' },
};

export const Support = {
  args: {
    variant: 'support',
    title: 'Support access',
    children: 'Cascadia support (J. Moreno) is viewing Riverbend CDFI read-only · approved by Alex Chen',
    aside: (
      <>
        Ends in 1 h 42 min <Button>End session</Button>
      </>
    ),
  },
};

export const SupportEnding = {
  name: 'Support ending (last hour)',
  args: {
    variant: 'supportEnding',
    title: '▲ Support access ends in 8 min',
    children: 'Last-hour warning: the banner inverts and the countdown shows minutes.',
  },
};

export const Audit = {
  args: {
    variant: 'audit',
    title: 'Read-only audit access',
    children: 'Granted by Alex Chen to Priya Nair, Halloway & Co. CPAs',
    aside: 'Expires Nov 15, 2026',
  },
};

export const RunInProgress = {
  name: 'Info (run in progress)',
  args: {
    variant: 'info',
    title: '◐ Run in progress',
    children:
      'Dana Ortiz started the Q3 2026 waterfall run at 10:02. New runs are locked until it is executed or discarded.',
    aside: <a href="#run">Open run</a>,
  },
};

export const SyncFailed = {
  name: 'Error (servicer sync failed)',
  args: {
    variant: 'error',
    title: '✕ Servicer sync failed',
    children:
      'LoanPro webhook returned 401. Last good sync Oct 7, 2026 at 23:40. Events after that time are missing.',
    aside: <Button>Resync</Button>,
  },
};
