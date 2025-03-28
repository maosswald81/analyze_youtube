import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient('https://your-supabase-url', 'your-supabase-anon-key');

export default function Home() {
  const [segments, setSegments] = useState([]);

  useEffect(() => {
    const fetchTranscriptions = async () => {
      const { data, error } = await supabase.from('transcriptions').select('*');
      if (error) console.error('Error fetching transcriptions:', error);
      else setSegments(data);
    };
    fetchTranscriptions();
  }, []);

  return (
    <div>
      <h1>Transcription Segments</h1>
      <ul>
        {segments.map((segment) => (
          <li key={segment.id}>
            <strong>{segment.start_time} - {segment.end_time}</strong>: {segment.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
