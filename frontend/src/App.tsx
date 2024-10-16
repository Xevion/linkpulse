import { useState, useEffect } from "react";

const Link = (props: JSX.IntrinsicElements['a']) => (
    <a
      className="text-pink-500 underline hover:no-underline dark:text-pink-400"
      {...props}
    />
  );

  const Code = (props: JSX.IntrinsicElements['code']) => (
    <code
      className="border-1 2py-1 font-light rounded border border-pink-500 bg-neutral-100 px-1 font-mono text-pink-500 dark:border-pink-400 dark:bg-neutral-700 dark:text-pink-400"
      {...props}
    />
  );
  
  export default function App() {
    const [time, setTime] = useState<string | null>(null);
    const [clientIp, setClientIp] = useState<string | null>(null);

    const refreshData = async () => {
      try {
        const response = await fetch('http://localhost:8000/');
        const data = await response.json();
        const { time, ip } = data;

        setTime(time);
        setClientIp(ip);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    // Refresh data on component mount and every 30 seconds
    useEffect(() => {
      refreshData();

      const interval = setInterval(() => {
        refreshData();
      }, 30 * 1000); 

      return () => clearInterval(interval);
    }, []);

    return (
      <div className="mx-auto my-8 mt-10 w-8/12 rounded border border-gray-200 p-4 shadow-md dark:border-neutral-600 dark:bg-neutral-800 dark:shadow-none">
        <h1 className="mb-4 text-4xl">LinkPulse</h1>
        <p className="mx-4 my-2">
          The current time is: <Code>{time || 'N/A'}</Code>
        </p>
        <p className="mx-4 my-2">
          Your IP address is: <Code>{clientIp || 'N/A'}</Code>
        </p>
      </div>
    );
  }