import { useEffect } from 'react';
import posthog from 'posthog-js';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    posthog.init('your-posthog-api-key', { api_host: 'https://app.posthog.com' });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
