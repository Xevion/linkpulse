import { useEffect, useState } from 'react';

const backendUrl = import.meta.env.PROD
  ? '/api'
  : `http://${import.meta.env.VITE_BACKEND_TARGET}/api`;

const Code = (props: JSX.IntrinsicElements['code']) => (
  <code
    className="border-1 2py-1 mx-1 rounded border border-pink-500 bg-neutral-100 px-1 font-mono font-light text-pink-500 dark:border-pink-400 dark:bg-neutral-700 dark:text-pink-400"
    {...props}
  />
);

type SeenIP = {
  last_seen: string;
  ip: string;
  count: number;
};

export default function App() {
  const [seenIps, setSeenIps] = useState<SeenIP[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refreshData = async () => {
    try {
      const response = await fetch(`${backendUrl}/ips`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();

      setSeenIps(data.ips);
      setError(null); // Clear any previous errors
      console.log('Data fetched:', data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError(error.message);
    }
  };

  // Refresh data on component mount and every 30 seconds
  useEffect(() => {
    refreshData();

    const interval = setInterval(
      () => {
        refreshData();
      },
      (import.meta.env.DEV ? 3 : 30) * 1000,
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-full min-w-full">
      <div className="mx-auto my-8 mt-10 w-8/12 max-w-md rounded border border-gray-200 p-4 shadow-md dark:border-neutral-600 dark:bg-neutral-800 dark:shadow-none">
        <h1 className="mb-4 text-3xl">LinkPulse</h1>

        {error && (
          <div className="mb-4 rounded border border-red-500 bg-red-100 p-2 text-red-700 dark:border-red-800/50 dark:bg-red-950/50 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="relative overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-500 rtl:text-right dark:text-gray-300">
            <tbody>
              {seenIps.map((ip) => (
                <tr key={ip.ip} className="border-b last:border-0 bg-white dark:border-neutral-700 dark:bg-neutral-800">
                  <td className="py-4">
                    <Code>{ip.ip}</Code>
                  </td>
                  <td className="py-4">
                    {ip.count} time{ip.count > 1 ? 's' : ''}
                  </td>
                  <td className="py-4">{ip.last_seen}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
