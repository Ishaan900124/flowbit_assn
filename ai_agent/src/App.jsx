import React, { useState, useEffect } from 'react';

function App() {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [allMemory, setAllMemory] = useState(null);

  useEffect(() => {
    document.title = 'AI Agent';
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setResult(null);
    setError(null);
    if (text && file) {
      alert('Please provide either text or a file, not both.');
      return;
    } else if (!text && !file) {
      alert('Please provide either text or a file.');
      return;
    }

    const formData = new FormData();
    if (file) {
      formData.append('fileInput', file);
    } else {
      formData.append('textInput', text);
    }

    fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        setResult(data);
      })
      .catch(err => {
        console.error(err);
        setError('Error during upload.');
      });
  };

  const handleFetchAllMemory = () => {
    fetch(`http://localhost:5000/get_all`)
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch all memory.');
        return response.json();
      })
      .then(data => {
        setAllMemory(data);
      })
      .catch(err => {
        console.error(err);
        setAllMemory(null);
        setError(err.message);
      });
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>AI Agent</h1>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Enter text:</label><br />
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows="4"
              cols="50"
              style={styles.textarea}
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Or upload a file:</label><br />
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              style={styles.input}
            />
          </div>
          <button type="submit" style={styles.button}>Submit</button>
        </form>

        {result && (
          <div style={styles.resultBox}>
            <h3>Result:</h3>
            <p><strong>Status:</strong> {result.status}</p>
            <p><strong>Format:</strong> {result.format}</p>
            <p><strong>Intent:</strong> {result.intent}</p>
            <p><strong>Thread ID:</strong> {result.thread_id}</p>
            <p><strong>Extracted Data:</strong></p>
            <pre style={styles.pre}>{JSON.stringify(result.extracted_data, null, 2)}</pre>
          </div>
        )}

        <div style={styles.memorySection}>
          <h3>Retrieve All Memory</h3>
          <button onClick={handleFetchAllMemory} style={styles.button}>Fetch All Memory</button>

          {allMemory && (
            <div style={styles.resultBox}>
              <h4>All Memory Data</h4>
              <pre style={styles.pre}>{JSON.stringify(allMemory, null, 2)}</pre>
            </div>
          )}
        </div>

        {error && (
          <div style={{ color: 'red', marginTop: '20px' }}>{error}</div>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'flex-start',
    width: '100vw',
    backgroundColor: '#f0f4f8',
    padding: '20px',
    minHeight: '100vh',
  },
  container: {
    textAlign: 'center',
    width: '100%',
    maxWidth: '700px',
  },
  title: {
    fontSize: '2.5rem',
    marginBottom: '20px',
    color: '#333',
    fontFamily: 'Arial, sans-serif',
  },
  form: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '12px',
    boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
    width: '100%',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  field: {
    marginBottom: '15px',
    width: '100%',
  },
  label: {
    fontWeight: 'bold',
    color: 'black',
    display: 'block',
    marginBottom: '5px',
    textAlign: 'left',
  },
  textarea: {
    width: '90%',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    fontSize: '1rem',
    backgroundColor: 'white',
    color: 'black',
  },
  input: {
    width: '90%',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    fontSize: '1rem',
  },
  button: {
    width: '90%',
    padding: '10px',
    backgroundColor: 'green',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    fontSize: '1rem',
    cursor: 'pointer',
    marginTop: '10px',
  },
  resultBox: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: 'green',
    color: 'white',
    borderRadius: '8px',
    textAlign: 'left',
  },
  pre: {
    backgroundColor: '#f5f5f5',
    padding: '10px',
    color: 'black',
    borderRadius: '6px',
    overflowX: 'auto',
  },
  memorySection: {
    marginTop: '30px',
    padding: '15px',
    backgroundColor: '#fff',
    borderRadius: '12px',
    boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
  }
};

export default App;